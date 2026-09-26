#!/usr/bin/env python3
"""
Agente autónomo "un centavo desde cero".

Pipeline de punta a punta, sin dependencias externas (solo stdlib):

  1. Billetera   — genera una dirección Bitcoin mainnet P2WPKH (bc1q...) con
                   secp256k1 + bech32 implementados aquí. La clave privada se
                   guarda en centavo/.wallet/ (ignorado por git), nunca en el repo.
  2. Mapeo       — sondea en vivo cada fuente candidata de valor y la clasifica
                   (captcha, login/KYC, caída, valor nulo, prohibida por política).
  3. Decisión    — solo acepta fuentes legales, sin evadir anti-bots, sin cuentas
                   ni identidad humana, y con valor de mercado > 0.
  4. Ejecución   — si alguna fuente pasa el filtro, la usa; si no, se detiene.
  5. Verificación— consulta el saldo real de la dirección en la blockchain y lo
                   convierte a USD con el precio de mercado actual.

Cada paso queda en centavo/logs/auditoria.jsonl.
"""
import datetime as dt
import hashlib
import json
import os
import re
import secrets
import ssl
import sys
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DIR_WALLET = os.path.join(AQUI, ".wallet")
DIR_LOGS = os.path.join(AQUI, "logs")
LOG = os.path.join(DIR_LOGS, "auditoria.jsonl")
DESTINO = os.path.join(AQUI, "destino.txt")
META_USD = 0.01
UA = "Mozilla/5.0 (X11; Linux x86_64) centavo-agent/1.0"


# ── auditoría ──────────────────────────────────────────────────────────────

def audit(fase, evento, **datos):
    reg = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "fase": fase, "evento": evento, **datos}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    print(f"[{reg['ts']}] {fase:<13} {evento}" +
          (f"  {json.dumps(datos, ensure_ascii=False)}" if datos else ""))


# ── HTTP ───────────────────────────────────────────────────────────────────

def _ctx():
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    return ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()


def http_get(url, timeout=15, headers=None, data=None):
    """Devuelve (status, cuerpo_texto). Nunca lanza por errores de red."""
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return r.status, r.read(2_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(200_000).decode("utf-8", "replace")
    except Exception as e:  # timeout, DNS, TLS...
        return 0, f"{type(e).__name__}: {e}"


def http_post(url, payload):
    return http_get(url, data=json.dumps(payload).encode(),
                    headers={"Content-Type": "application/json"})


def http_json(url, reintentos=3):
    for intento in range(1, reintentos + 1):
        st, body = http_get(url)
        if st == 200:
            try:
                return json.loads(body)
            except ValueError:
                pass
        audit("red", "reintento", url=url, status=st, intento=intento)
    return None


# ── billetera: secp256k1 + hash160 + bech32 (BIP-173) ──────────────────────

P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)


def _add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if a[0] == b[0] and (a[1] + b[1]) % P == 0:
        return None
    if a == b:
        m = 3 * a[0] * a[0] * pow(2 * a[1], -1, P) % P
    else:
        m = (b[1] - a[1]) * pow(b[0] - a[0], -1, P) % P
    x = (m * m - a[0] - b[0]) % P
    return x, (m * (a[0] - x) - a[1]) % P


def _mul(k, pt=G):
    acc = None
    while k:
        if k & 1:
            acc = _add(acc, pt)
        pt = _add(pt, pt)
        k >>= 1
    return acc


_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _polymod(vals):
    gen = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in vals:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= gen[i] if (top >> i) & 1 else 0
    return chk


def _bech32(hrp, data):
    exp = [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]
    pm = _polymod(exp + data + [0] * 6) ^ 1
    chk = [(pm >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(_CHARSET[d] for d in data + chk)


def _bits8to5(data):
    acc = bits = 0
    out = []
    for b in data:
        acc = (acc << 8) | b
        bits += 8
        while bits >= 5:
            bits -= 5
            out.append((acc >> bits) & 31)
    if bits:
        out.append((acc << (5 - bits)) & 31)
    return out


def direccion_desde_clave(priv):
    x, y = _mul(priv)
    pub = bytes([2 + (y & 1)]) + x.to_bytes(32, "big")
    h160 = hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()
    return _bech32("bc", [0] + _bits8to5(h160)), pub.hex()


def autotest_billetera():
    # Vector de BIP-173: clave pública comprimida de la clave privada = 1.
    addr, pub = direccion_desde_clave(1)
    assert pub == "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798"
    assert addr == "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", addr


def obtener_billetera():
    os.makedirs(DIR_WALLET, mode=0o700, exist_ok=True)
    ruta = os.path.join(DIR_WALLET, "clave.json")
    if os.path.exists(ruta):
        with open(ruta) as f:
            w = json.load(f)
        audit("billetera", "reutilizada", direccion=w["direccion"])
        return w
    # En un contenedor nuevo la clave local no existe: se usa la dirección ya
    # publicada (su clave la custodia el dueño) en vez de crear otra.
    if os.path.exists(DESTINO):
        with open(DESTINO) as f:
            addr = f.read().strip()
        audit("billetera", "dirección fija (clave en custodia del dueño)", direccion=addr)
        return {"direccion": addr}
    priv = secrets.randbelow(N - 1) + 1
    addr, pub = direccion_desde_clave(priv)
    w = {"red": "bitcoin-mainnet", "tipo": "P2WPKH", "direccion": addr,
         "clave_publica": pub, "clave_privada_hex": f"{priv:064x}"}
    fd = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(w, f, indent=2)
    audit("billetera", "generada", direccion=addr, clave_privada="(guardada en .wallet/, fuera de git)")
    return w


# ── mapeo de fuentes de valor ──────────────────────────────────────────────

# (nombre, url a sondear, tiene valor de mercado, bloqueo por política o None)
FUENTES = [
    ("Faucet BTC testnet4 (faucet.testnet4.dev)", "https://faucet.testnet4.dev/", False, None),
    ("Faucet BTC testnet (coinfaucet.eu)", "https://coinfaucet.eu/en/btc-testnet/", False, None),
    ("Faucet ETH Sepolia (Alchemy)", "https://www.alchemy.com/faucets/ethereum-sepolia", False, None),
    ("Faucet ETH Sepolia (sepoliafaucet.com)", "https://sepoliafaucet.com/", False, None),
    ("Micro-faucets mainnet (FaucetPay)", "https://faucetpay.io/", True, None),
    ("Faucet BTC mainnet (freebitco.in)", "https://freebitco.in/", True, None),
    ("Faucet Lightning (lightningfaucet.com)", "https://lightningfaucet.com/", True, None),
    ("Faucet Nano (faucet.xnopay.com)", "https://faucet.xnopay.com/", True, None),
    ("Faucet Nano (freenanofaucet.com)", "https://freenanofaucet.com/", True, None),
    ("Faucet Nano (nanospace.fun)", "https://nanospace.fun/", True, None),
    ("The Nano Button (thenanobutton.com)", "https://thenanobutton.com/", True, None),
    ("Minería CPU (p.ej. Monero/RandomX) en este contenedor", None, True,
     "usar cómputo de un proveedor cloud ajeno para minar no está autorizado"),
    ("Resolver captchas con servicios/IA para cobrar faucets", None, True,
     "evadir controles anti-bot viola los términos de cada sitio"),
    ("Bounties de código (GitHub/Algora) y micro-tareas pagas", None, True,
     "el cobro exige identidad humana verificada (KYC / Stripe / PayPal)"),
]

PATRONES_CAPTCHA = re.compile(r"h-?captcha|recaptcha|turnstile|cf-chl|captcha", re.I)
PATRONES_LOGIN = re.compile(r"sign[ -]?in|log[ -]?in|iniciar sesi|register|kyc", re.I)


def captcha_en_scripts(url, html, maximo=20):
    """Muchos faucets montan el captcha desde el bundle JS, no desde el HTML."""
    origen = re.match(r"https?://[^/]+", url).group(0)
    srcs = re.findall(r'src="(/[^"]+\.js)[^"]*"', html)
    for src in srcs[:maximo]:
        st, js = http_get(origen + src)
        if st == 200 and PATRONES_CAPTCHA.search(js):
            return True
    return False


def clasificar(nombre, url, valor, politica):
    if politica:
        return {"fuente": nombre, "viable": False, "motivo": f"descartada por política: {politica}"}
    st, body = http_get(url)
    señales = []
    if st == 0 or st >= 500:
        señales.append(f"inaccesible (HTTP {st})")
    if PATRONES_CAPTCHA.search(body):
        señales.append("exige captcha")
    elif st == 200 and captcha_en_scripts(url, body):
        señales.append("exige captcha (cargado desde su JavaScript)")
    if PATRONES_LOGIN.search(body):
        señales.append("exige cuenta/login")
    if st in (301, 302, 403) and not señales:
        señales.append(f"redirección/bloqueo anti-bot (HTTP {st})")
    if not valor:
        señales.append("activo de testnet: valor de mercado $0 por diseño")
    return {"fuente": nombre, "url": url, "http": st, "viable": not señales,
            "motivo": "; ".join(señales) or "sin bloqueos detectados"}


# ── sondas por API (estado real, no solo la portada) ───────────────────────
# Cada sonda devuelve el mismo formato que clasificar(). "oportunidad" marca una
# fuente legítima que hoy no paga sola pero conviene revisar en cada corrida.

def _precio(coin):
    p = http_json(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd")
    return p[coin]["usd"] if p else None


def sonda_nanodrop():
    """NanoDrop expone /api/status: monto por reclamo y si exige hCaptcha."""
    nombre = "Faucet Nano (nanodrop.io, API /api/status)"
    st = http_json("https://nanodrop.io/api/status")
    xno = _precio("nano")
    if st is None or xno is None:
        return {"fuente": nombre, "viable": False, "motivo": "API o precio no disponibles"}
    usd = float(st["amountNano"]) * xno
    señales = []
    if st.get("verificationRequired"):
        señales.append("exige hCaptcha")
    if usd < META_USD:
        señales.append(f"un reclamo = {st['amountNano']} XNO ≈ USD {usd:.6f}; "
                       f"llegar a USD {META_USD} exigiría {int(META_USD / usd) + 1} reclamos "
                       "(abuso del faucet, pensado para uno por persona)")
    return {"fuente": nombre, "viable": not señales, "motivo": "; ".join(señales) or "ok"}


def sonda_taskbounty():
    """TaskBounty: bugs reales verificados por tests, pago cripto automático."""
    nombre = "Bounties para agentes (task-bounty.com, API /api/v1/tasks)"
    d = http_json("https://www.task-bounty.com/api/v1/tasks")
    if d is None:
        return {"fuente": nombre, "viable": False, "motivo": "API no disponible"}
    n = len(d.get("data") or [])
    return {"fuente": nombre, "viable": False, "oportunidad": n > 0,
            "motivo": f"{n} tareas abiertas; el registro del operador exige una cuenta humana"}


def sonda_superteam():
    """Superteam Earn: API oficial para agentes (registro sin humano)."""
    nombre = "Bounties para agentes (Superteam Earn, API /api/agents)"
    ruta = os.path.join(DIR_WALLET, "superteam.json")
    key = os.environ.get("SUPERTEAM_API_KEY")
    if not key and os.path.exists(ruta):
        with open(ruta) as f:
            key = json.load(f)["apiKey"]
    if not key and os.environ.get("CENTAVO_REGISTRAR") == "1":
        st, body = http_post("https://superteam.fun/api/agents", {"name": "centavo-agent"})
        if st not in (200, 201):
            return {"fuente": nombre, "viable": False, "motivo": f"registro falló (HTTP {st})"}
        os.makedirs(DIR_WALLET, mode=0o700, exist_ok=True)
        fd = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(body)
        key = json.loads(body)["apiKey"]
        audit("mapeo", "agente registrado en Superteam Earn", username=json.loads(body)["username"])
    if not key:
        # No se registra un agente nuevo en cada contenedor efímero.
        return {"fuente": nombre, "viable": False,
                "motivo": "sin API key (defina SUPERTEAM_API_KEY, o CENTAVO_REGISTRAR=1 para registrar uno)"}
    st, body = http_get("https://superteam.fun/api/agents/listings/live?take=50",
                        headers={"Authorization": f"Bearer {key}"})
    if st != 200:
        return {"fuente": nombre, "viable": False, "motivo": f"API respondió HTTP {st}"}
    n = len(json.loads(body))
    return {"fuente": nombre, "viable": False, "oportunidad": n > 0,
            "motivo": f"{n} listados abiertos a agentes; ganar depende del jurado del sponsor "
                      "y el cobro lo reclama un humano con el claimCode"}


def sonda_anclas_p2a():
    """Salidas Pay-to-Anchor (bc1pfeessrawgf): 'anyone-can-spend' por protocolo."""
    nombre = "Salidas anyone-can-spend de Bitcoin (Pay-to-Anchor)"
    d = http_json("https://mempool.space/api/address/bc1pfeessrawgf")
    if d is None:
        return {"fuente": nombre, "viable": False, "motivo": "API no disponible"}
    cs, ms = d["chain_stats"], d["mempool_stats"]
    libres = cs["funded_txo_sum"] - cs["spent_txo_sum"]
    en_disputa = ms["spent_txo_sum"] - ms["funded_txo_sum"]
    return {"fuente": nombre, "viable": False,
            "motivo": f"{cs['funded_txo_count']} salidas históricas, {cs['spent_txo_count']} ya barridas; "
                      f"{libres} sats sin gastar en cadena y {max(en_disputa, 0)} sats ya en disputa en mempool. "
                      "Son el mecanismo de ajuste de comisión (CPFP) de otros: competir por ellas "
                      "sabotea su transacción, así que se descarta"}


SONDAS = [sonda_nanodrop, sonda_taskbounty, sonda_superteam, sonda_anclas_p2a]


# ── verificación on-chain ──────────────────────────────────────────────────

def saldo_usd(direccion):
    info = http_json(f"https://mempool.space/api/address/{direccion}")
    precio = http_json("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
    if info is None or precio is None:
        return None
    cs, ms = info["chain_stats"], info["mempool_stats"]
    sats = (cs["funded_txo_sum"] - cs["spent_txo_sum"]
            + ms["funded_txo_sum"] - ms["spent_txo_sum"])
    btc_usd = precio["bitcoin"]["usd"]
    return {"sats": sats, "btc_usd": btc_usd, "usd": sats / 1e8 * btc_usd,
            "txs": cs["tx_count"] + ms["tx_count"]}


# ── orquestación ───────────────────────────────────────────────────────────

def main():
    os.makedirs(DIR_LOGS, exist_ok=True)
    audit("inicio", "ejecución", meta_usd=META_USD, python=sys.version.split()[0])

    autotest_billetera()
    audit("billetera", "autotest BIP-173 OK")
    w = obtener_billetera()

    audit("mapeo", "sondeando fuentes", total=len(FUENTES))
    resultados = [clasificar(*f) for f in FUENTES] + [sonda() for sonda in SONDAS]
    for r in resultados:
        estado = "viable" if r["viable"] else "oportunidad" if r.get("oportunidad") else "descartada"
        audit("mapeo", estado, fuente=r["fuente"], motivo=r["motivo"])

    viables = [r for r in resultados if r["viable"]]
    oportunidades = [r["fuente"] for r in resultados if r.get("oportunidad")]
    audit("decisión", "fuentes viables", cantidad=len(viables), oportunidades=oportunidades)
    if viables:
        # Punto de extensión: aquí iría el reclamo automático de la fuente viable.
        audit("ejecución", "fuente viable sin integrador implementado",
              fuentes=[r["fuente"] for r in viables])
    else:
        audit("ejecución", "no hay ruta legal y sin intervención humana; no se reclama nada")

    s = saldo_usd(w["direccion"])
    if s is None:
        audit("verificación", "no se pudo consultar saldo/precio")
        estado = "INDETERMINADO"
    else:
        audit("verificación", "saldo on-chain", direccion=w["direccion"], **s)
        estado = "LOGRADO" if s["usd"] >= META_USD else "NO LOGRADO"
    audit("fin", f"meta {META_USD} USD: {estado}", direccion=w["direccion"])

    with open(os.path.join(DIR_LOGS, "resultado.json"), "w", encoding="utf-8") as f:
        json.dump({"estado": estado, "direccion": w["direccion"], "saldo": s,
                   "fuentes": resultados}, f, indent=2, ensure_ascii=False)
    return 0 if estado == "LOGRADO" else 1


if __name__ == "__main__":
    sys.exit(main())
