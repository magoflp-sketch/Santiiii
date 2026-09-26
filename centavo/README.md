# Agente "un centavo desde cero"

Intento de que un sistema 100% autónomo, sin capital inicial ni intervención humana,
genere **USD 0,01** y lo deposite en una billetera propia.

**Resultado: NO LOGRADO.** Saldo verificado on-chain: **0 sats = USD 0,00**.
No se fabricó ningún comprobante: la dirección puede consultarse públicamente.

- Dirección de destino (Bitcoin mainnet, P2WPKH):
  `bc1qj2f75ef72llucsm87wmvw3r4m4zv3mcguyccac`
  — https://mempool.space/address/bc1qj2f75ef72llucsm87wmvw3r4m4zv3mcguyccac
- La dirección está fijada en `destino.txt`. La clave privada (formato WIF, importable
  en Electrum/Sparrow como `p2wpkh`) se le entregó al dueño y nunca se sube al repo:
  una clave en un repo público permite que cualquiera vacíe la dirección. En un
  contenedor nuevo el agente no crea otra billetera; verifica esta dirección.

## Cómo correrlo

```sh
python3 centavo/agente.py   # solo stdlib; exit 0 si la meta se cumple, 1 si no
```

Genera `logs/auditoria.jsonl` (registro paso a paso) y `logs/resultado.json`.

## Método

1. **Billetera**: secp256k1 + hash160 + bech32 implementados en el script; autotest
   contra el vector de BIP-173 antes de generar la clave (`secrets`, CSPRNG).
2. **Mapeo en vivo** de cada fuente candidata: se descarga su página **y sus bundles
   JavaScript** (varios faucets cargan el captcha desde ahí, p. ej. XNOPay con hCaptcha
   invisible) y se detectan captcha, login/KYC, caídas y activos sin valor. Donde hay
   API pública se consulta el estado real (`sonda_*` en `agente.py`).
3. **Filtro de decisión**: solo pasan fuentes legales, que no requieran evadir
   anti-bots, que no requieran identidad humana y cuyo activo tenga valor > 0.
4. **Verificación**: saldo real vía API de mempool.space × precio BTC/USD de CoinGecko.

## Por qué ninguna vía pasó el filtro

| Vía | Bloqueo |
|---|---|
| Faucets de testnet (BTC testnet4, Sepolia) | Captcha, y además el activo vale $0 por diseño: no cuenta como dólar. |
| Micro-faucets mainnet (FaucetPay, Lightning Faucet) | Captcha (hCaptcha/reCAPTCHA/Turnstile) + cuenta. |
| freebitco.in | Inaccesible (HTTP 502) al momento de la prueba. |
| Faucets Nano: XNOPay, FreeNanoFaucet, NanoSpace, The Nano Button | hCaptcha / reCAPTCHA / Turnstile (+ PoW Altcha en Nano Button). XNOPay da 0,00001 XNO ≈ USD 0,000004. |
| NanoDrop (API `/api/status`) | `verificationRequired: true` (hCaptcha) y 0,0001 XNO ≈ USD 0,000038 por reclamo: harían falta ~265 reclamos, abuso de un faucet de uno por persona. |
| TaskBounty (bugs reales, pago cripto automático) | API pública con 0 tareas abiertas; el operador del agente se registra con cuenta humana. |
| Superteam Earn, API oficial para agentes | Registro por API sin humano (hecho: agente `centavo-agent-communist-21`). 0 listados abiertos a agentes hoy. Si gana, el pago lo reclama un humano con el `claimCode`. |
| Salidas *anyone-can-spend* de Bitcoin (Pay-to-Anchor `bc1pfeessrawgf`) | 4,77 M salidas históricas, todas barridas salvo 822 sats que ya se están gastando en mempool. Son el ajuste de comisión (CPFP) de terceros: competir por ellas les sabotea la transacción. |
| Resolver captchas con IA/servicios | Es evadir un control anti-bot: viola los términos de cada sitio. |
| Minería CPU en este contenedor | El cómputo es de un proveedor cloud que no lo autoriza; además los pools tienen umbrales de pago muy por encima de un centavo. |
| Bounties de código / micro-tareas (MTurk, Algora, etc.) | El cobro exige identidad verificada (KYC, Stripe, PayPal): requiere a una persona. |

Conclusión: todas las fuentes de dinero real accesibles por API pública están
diseñadas justamente para exigir a un humano (captcha, cuenta o KYC). Las que no lo
exigen entregan activos de prueba sin valor. Con las restricciones "cero intervención
humana" + "legal" + "sin inversión", la meta no se puede cumplir honestamente.

## Seguimiento

El agente vuelve a correr y marca como **oportunidad** cualquier fuente legítima que
se abra (p. ej. un listado para agentes en Superteam o una tarea en TaskBounty).
Variables: `SUPERTEAM_API_KEY` (usa el agente ya registrado) o `CENTAVO_REGISTRAR=1`
(registra uno; por defecto no, para no crear una cuenta por cada contenedor efímero).

## Qué sí la destrabaría (requiere a una persona)

- Una cuenta propia en un servicio de pagos (Lightning wallet con API, FaucetPay,
  etc.) donde un humano resuelva el captcha o pase el KYC una vez; o
- Vender un trabajo real (p.ej. una de las páginas de este repo como plantilla) y
  cobrarlo a la dirección de arriba.

`agente.py` tiene un punto de extensión en la fase de ejecución para enchufar esa
fuente si aparece; la verificación on-chain ya funciona sola.
