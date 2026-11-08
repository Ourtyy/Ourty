# Guía Ourty: de cero a ganar dinero con anuncios

## Cómo funciona el sitio
- Los artículos están en `content/drafts/` (borradores) y `content/posts/` (publicados).
- `python3 build.py preview` genera la vista previa con borradores (carpeta `preview/`).
- `python3 build.py publish <nombre>` publica un borrador y genera el sitio final (carpeta `docs/`).
- Cuando el sitio esté conectado a GitHub, cada publicación se sube sola y la web se actualiza en 1–2 minutos.
- Las páginas legales (Sobre nosotros, Aviso médico, Privacidad, Contacto) ya están hechas: AdSense las exige.
- Hay un menú "Translate" en cada página que abre la web traducida con Google Translate (español, francés, árabe...).

---

## Paso 1 — Revisa los primeros artículos (hoy)
Hay 4 borradores listos:
1. How Much Exercise Do You Really Need? (Fitness)
2. How Much Sleep Do Adults Really Need? (Sleep)
3. A 5-Minute Breathing Exercise for Stressful Days (Mind)
4. Easy Overnight Oats (Recipes)

Léelos y dime "publica el 1 y el 3" o "cambia esto en el 2".

## Paso 2 — Crea tu cuenta de GitHub (5 min, gratis)
1. Entra en https://github.com/signup
2. Usa tu email, una contraseña segura y un nombre de usuario (por ejemplo `ourty-blog`).
3. Confirma el email.
4. Dime tu nombre de usuario. **Nunca me des la contraseña.**

## Paso 3 — Comprar el dominio (cuando tengas ~11 €)

### 3.1 Elegir el nombre
- `ourty.com` está cogido. Libres (comprobado el 8/11/2026): **getourty.com**, **ourtyhealth.com**, **ourty.co**.
- Recomendado: un **.com**, que es el que más confianza da y el más barato de renovar (~10–12 €/año). El .co es bastante más caro.
- Evita las ofertas de "1 € el primer año" (.xyz, .site, .online): luego renuevan a 20–40 €.

### 3.2 Comprarlo en Porkbun (recomendado: barato, en inglés sencillo y privacidad gratis)
1. Entra en https://porkbun.com
2. Escribe el nombre (por ejemplo `getourty`) en el buscador grande y pulsa la lupa.
3. Busca la fila del **.com** y pulsa el carrito 🛒. Fíjate en el precio de **renovación** (renewal), no solo en el del primer año.
4. Arriba a la derecha pulsa **Checkout**.
5. Te pedirá **crear una cuenta**: email, contraseña y tus datos (nombre, dirección, teléfono). Es obligatorio por ley para registrar dominios, pero Porkbun los oculta gratis (**WHOIS Privacy**: déjalo activado).
6. Duración: **1 año** basta. Puedes activar la **renovación automática (auto-renew)** para no perder el dominio nunca.
7. Paga con tarjeta o PayPal. **Esto lo haces tú.**
8. Recibirás un email de confirmación. ¡El dominio es tuyo!

> Alternativa igual de buena: **Cloudflare Registrar** (https://dash.cloudflare.com), que vende al precio de coste, pero el panel es más técnico.

### 3.3 Conectar el dominio a la web (te guío yo en directo)
En Porkbun: **Account → Domain Management → tu dominio → DNS**. Hay que borrar los registros que trae por defecto y añadir estos:

| Tipo | Host | Valor |
|---|---|---|
| A | (vacío) | 185.199.108.153 |
| A | (vacío) | 185.199.109.153 |
| A | (vacío) | 185.199.110.153 |
| A | (vacío) | 185.199.111.153 |
| CNAME | www | ourtyy.github.io |

Después:
1. Yo cambio la configuración de la web al dominio nuevo y la subo.
2. Tú, en https://github.com/Ourtyy/Ourty/settings/pages, escribes el dominio en **Custom domain** y pulsas **Save**.
3. Esperas entre 15 minutos y 24 horas a que se active, y marcas **Enforce HTTPS** (el candado 🔒).

## Paso 4 — Conectamos el sitio a internet (lo hacemos juntos)
- Yo creo el repositorio y configuro GitHub Pages (hosting gratis).
- Tú solo tendrás que iniciar sesión en GitHub una vez desde tu Mac cuando te lo pida.
- Configuramos el dominio y el HTTPS gratuito.

## Paso 5 — Llenar el sitio de contenido (2–4 semanas)
- Objetivo: **20–25 artículos publicados** antes de pedir AdSense.
- Yo te preparo lotes de borradores; tú revisas y apruebas.

## Paso 6 — Google Search Console (10 min, gratis)
Para que Google encuentre tu web:
1. https://search.google.com/search-console → añadir tu dominio.
2. Te guío para verificarlo y enviar el `sitemap.xml` (ya se genera solo).

## Paso 7 — Solicitar Google AdSense
1. https://adsense.google.com → regístrate con tu cuenta de Google y añade tu dominio.
2. Pon tus datos de pago **tú** (yo no puedo meter datos bancarios).
3. Dame tu ID de editor (`ca-pub-XXXXXXXX`). Yo lo pongo en la web y creo el `ads.txt`.
4. En AdSense, activa **Privacidad y mensajes → mensaje del RGPD** (obligatorio para visitantes de Europa).
5. La revisión tarda de unos días a unas semanas.

## Paso 8 — Piloto automático: un artículo cada 3 días
- Una tarea programada escribe un borrador nuevo cada 3 días.
- Te aviso, tú lo lees y me dices "publica" o pides cambios.
- Se publica y la web se actualiza.

---

## Expectativas realistas
- Los primeros meses las visitas serán bajas; Google tarda en confiar en una web nueva.
- El inglés es buena elección: los anuncios en EE. UU./Reino Unido pagan más que en otros mercados.
- Lo que más ayuda a crecer: constancia, artículos útiles de verdad y compartirlos (Pinterest funciona muy bien para recetas y bienestar).
