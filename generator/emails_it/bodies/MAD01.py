# MAD01 Madrid Calle Serrano - hand-written closing emails (Spanish). Bodies are authored one by one.

PERSONAS = {
    "lucia": "Lucía Fernández Ortega <lucia.fernandez@moncler-retail.example>",
    "javier": "Javier Molina <javier.molina@moncler-retail.example>",
    "martina": "Martina Echeverría <martina.echeverria@moncler-retail.example>",
    "store": "Moncler Madrid Serrano <mad01.store@moncler-retail.example>",
    "roberto": "Roberto Galli <roberto.galli@moncler-retail.example>",
    "ops": "retail-ops-spain@moncler-retail.example",
    "opsit": "retail-ops-italy@moncler-retail.example",
    "dc": "dc-replenishment@moncler-retail.example",
    "merch": "merch-planning@moncler-retail.example",
    "it": "it-helpdesk@moncler-retail.example",
}
DEFAULT_TO = ["ops"]
DEFAULT_CC = ["roberto"]

EMAILS = [
    dict(id="c0831", sent="2026-08-31 21:52", frm="javier", subject="cierre 31/08", business_date="2026-08-31",
         body="""Buenas,

cierre de hoy: 4,8k vs 11,2 de ppto. Malo malo.
75 personas por la puerta y 6 tickets, la mitad entraba a por el aire acondicionado jaja. Madrid sigue medio vacio, la gente vuelve este finde.

Una clienta pregunto por el Albenga negro en talla 2, no tenemos ni 0 ni 1 ni 2. Si alguien sabe si entra algo genial.

Mañana vuelve Lucia.
Javi

Enviado desde mi iPhone"""),

    dict(id="ooo0831", sent="2026-08-31 21:53", frm="roberto", to=["javier"], cc=[], kind="ooo",
         reply_to_id="c0831", suffix="_ooo", subject="Risposta automatica: cierre 31/08",
         headers={"Auto-Submitted": "auto-replied", "X-Autoreply": "yes"},
         body="""Sono fuori ufficio con accesso limitato alla posta fino a venerdì 4 settembre. Per urgenze contattare retail-ops-italy@moncler-retail.example.

I am out of office with limited access to email until Friday 4 September. For urgent matters please contact retail-ops-italy@moncler-retail.example.

Roberto Galli
Area Manager Italy & Spain"""),

    dict(id="c0901", sent="2026-09-01 21:34", frm="lucia", subject="Cierre MAD01 - 01/09", business_date="2026-09-01",
         body="""Buenas noches,

Os paso el cierre de hoy.

RESUMEN CIERRE
Venta neta: 7.790 €
Ppto: 10.530 € (-26%)
Tráfico: 77 | Conv.: 10,4%
Tickets: 8 | UPT: 1,4
Comentarios: día tranquilo, primera semana de septiembre y mucha gente todavía fuera. Lo que se mueve es punto y accesorios (gorros con logo, cardigan logo negro). Con 35 grados nadie se prueba un plumas. Algunos americanos por la mañana.
Stock: seguimos sin sudadera con capucha negra en M ni la de cuello redondo negra en M, a ver si entran en el envío del jueves.

Un saludo,
Lucía
--
Lucía Fernández Ortega
Store Manager | Moncler Madrid Serrano
Este mensaje es confidencial y va dirigido exclusivamente a sus destinatarios."""),

    dict(id="c0902", sent="2026-09-02 21:41", frm="lucia", subject="Cierre MAD01 - 02/09", business_date="2026-09-02",
         body="""Hola a todos,

RESUMEN CIERRE
Venta neta: 12.920 €
Ppto: 11.990 € (+8%)
Tráfico: 71 | Conv.: 9,9%
Tickets: 7 | UPT: 1,7
Comentarios: mejor de lo esperado con muy poca gente. Dos tickets buenos de clientes mexicanos (sudaderas con capucha en tres colores, para toda la familia) y una pareja de Texas.
Peticiones sin stock: Hermine azul marino talla 0, Peyre negro talla 2 y un polo blanco XS. La Hermine navy en 0 la piden bastante, ¿hay posibilidad de transfer desde otra tienda?

Gracias,
Lucía"""),

    dict(id="c0903", sent="2026-09-03 21:28", frm="lucia", subject="Cierre MAD01 - 03/09", business_date="2026-09-03",
         body="""Buenas noches,

RESUMEN CIERRE
Venta neta: 7.140 €
Ppto: 16.700 € (-57%)
Tráfico: 90 | Conv.: 6,7%
Tickets: 6 | UPT: 1,2
Comentarios:
- Envío recibido esta mañana a su hora, 120 piezas, casi todo punto, camisetas y accesorios. Ya está dado de alta en sistema.
- Una devolución de un chaleco Tib talla 3, el cliente cambió de idea (era un regalo que no gustó).
- Una clienta quería las Trailgrip de mujer negras en 37 y no nos queda ninguna.
Día muy flojo, otra vez calor fuerte por la tarde. Esperamos que el fin de semana se anime.

Lucía"""),

    dict(id="c0904", sent="2026-09-04 21:47", frm="lucia", subject="Cierre MAD01 - 04/09", business_date="2026-09-04",
         body="""Buenas noches,

RESUMEN CIERRE
Venta neta: 16.635 €
Ppto: 19.710 € (-16%)
Tráfico: 129 | Conv.: 10,9%
Tickets: 14 | UPT: 1,5
Comentarios: primeros clientes latinoamericanos de la temporada, una familia de Bogotá y dos chicas argentinas, todos con tax free. Vendidas 3 Bady negras y 2 Maire negras (ojo que de la Maire negra nos queda muy poco).
Sin stock: Ilvaro blanco roto talla 4 y jersey de ochos blanco roto XS.

Roberto, bienvenido de vuelta el lunes :)

Lucía
--
Lucía Fernández Ortega
Store Manager | Moncler Madrid Serrano
Este mensaje es confidencial y va dirigido exclusivamente a sus destinatarios."""),

    dict(id="c0905", sent="2026-09-05 22:05", frm="lucia", subject="Cierre MAD01 - 05/09", business_date="2026-09-05",
         body="""Hola,

RESUMEN CIERRE
Venta neta: 16.075 €
Ppto: 26.170 € (-39%)
Tráfico: 178 | Conv.: 6,7%
Tickets: 12
Comentarios: sábado de mucho paseo y poca compra. Bastante gente en Serrano pero entran, miran y se van a El Corte Inglés. Un grupo de clientes chinos por la tarde que se llevó gorras y gorros. Los polos navy (3) siguen saliendo, el verano no se acaba.
Arneb negra talla 5 ya a cero.

Buen domingo,
Lucía"""),

    dict(id="c0906", sent="2026-09-06 21:12", frm="javier", subject="cierre domingo 6", business_date="2026-09-06",
         body="""Buenas!

9,8k vs 19 de ppto. Domingo de calor y de devoluciones:
- una Maire talla 3, la clienta dice q se le descosia el bolsillo, la aparto para calidad
- un gorro y una gorra x talla (los dos de la misma familia jaja)

Bastantes chinos y americanos, poco español. Nos hemos quedado sin Maire negra en talla 0.

Roberto vuelve mañana no? q se prepare
Javi"""),

    dict(id="c0907", sent="2026-09-07 21:36", frm="store", subject="Cierre Serrano lunes 07/09", business_date="2026-09-07",
         body="""Hola a todos!

Les escribo yo hoy desde el iPad de la tienda porque Javi se tuvo que ir antes (médico) y Lucía libra.

Venta 9.490 €, presupuesto 13.890. Entraron 96 personas según el contador.
Hoy casi todo colombianos y argentinos, mirá, parecía Palermo jaja. Una clienta de Medellín re linda buscaba la Maire negra en talla 0 y no tenemos, le dije que la anotaba y le escribía por WhatsApp apenas entre. Un señor de Buenos Aires quería la Karakorum negra en talla 2, tampoco.
Vendimos un Peyre negro, guantes y una riñonera Légère.

Saludos!
Martina E. (SA)"""),

    dict(id="c0908", sent="2026-09-08 22:10", frm="javier", subject="cierre martes", business_date="2026-09-08",
         body="""q dia!!

21,9k con 95 personas, +50% vs ppto. Conversion 12,6%
3 cardigan logo negro, un Valbourg negro y guantes. Clientes de aqui casi todos, gente q vuelve de vacaciones con ganas de gastar

Lo q no tenemos:
Maire negra talla 0 (2a vez en dos dias, ya son dos clientas)
Arneb negra talla 5
Insolux blanco roto 40

J."""),

    dict(id="c0910", sent="2026-09-10 21:31", frm="lucia", subject="Cierre MAD01 - 10/09", business_date="2026-09-10",
         body="""Buenas noches,

RESUMEN CIERRE
Venta neta: 21.310 €
Ppto: 18.590 € (+15%)
Tráfico: 123 | Conv.: 13,8%
Tickets: 17 | UPT: 1,2
Comentarios:
Envío del jueves recibido a su hora, 142 piezas. Muy buen día, muchos americanos (20% de los tickets más o menos) y argentinos.
Vendidas 2 Maire negras más, ya no queda casi nada en negro. 3 cardigan logo negro y 2 Trailgrip mujer.
Empiezan las preguntas por el Ambrine en marrón chocolate (el abrigo largo nuevo), tenemos muy pocas tallas en marrón.
Primeras Arneb vendidas: tallan grande, estamos aconsejando una talla menos.

Lucía"""),

    dict(id="c0911", sent="2026-09-11 21:22", frm="lucia", subject="Cierre MAD01 - 11/09", business_date="2026-09-11",
         body="""Hola,

Día flojo: 11.380 € vs 21.390 de ppto. 123 personas y solo 11 tickets, mucho turista mirando.
Otra vez nos piden el cardigan logo negro en XL y no hay.
Una devolución de un cardigan S, cambio de opinión.

Un saludo,
Lucía"""),

    dict(id="c0912", sent="2026-09-12 22:18", frm="lucia", subject="Cierre MAD01 - 12/09", business_date="2026-09-12",
         body="""Buenas noches,

RESUMEN CIERRE
Venta neta: 39.900 €
Ppto: 30.470 € (+31%)
Tráfico: 174 | Conv.: 11,5%
Tickets: 20 | UPT: 1,7
Comentarios: sábado muy bueno. 4 Bady negras, 3 Trailgrip mujer negras, 2 Tib negros. Mucho cliente internacional, argentinos otra vez (se nota que empieza su temporada de viajes) y algún americano.
De nuevo el cardigan logo negro XL, no lo tenemos y lo piden cada semana. ¿Podemos pedirlo a merch?

Lucía
--
Lucía Fernández Ortega
Store Manager | Moncler Madrid Serrano
Este mensaje es confidencial y va dirigido exclusivamente a sus destinatarios."""),

    dict(id="corr0912", sent="2026-09-13 10:12", frm="lucia", subject="Corrección cierre 12/09", kind="correction",
         suffix="_corr", reply_to_id="c0912", business_date="2026-09-12",
         body="""Buenos días,

perdón, ayer puse mal la venta del sábado: fueron 33.870 €, no 39.900. Contra ppto es +11%, no +31%. Lo demás está bien.

Lucía"""),

    dict(id="c0913", sent="2026-09-13 21:05", frm="javier", subject="cierre domingo", business_date="2026-09-13",
         body="""Buenas,

23,5k vs 19,3 de ppto, +22%. Domingo muy español, familias de barrio.
4 camisetas logo negras y 3 cuellos altos navy, en septiembre lo q manda es el algodón jaja

Sin stock:
- Ambrine marron chocolate talla 1 (la primera q me piden a mi)
- Rosiere negro talla 1
- polo blanco M

Lucia, se nos acaba la camiseta negra en M, mañana lo miro.
Javi

Enviado desde mi iPhone"""),

    dict(id="c0914", sent="2026-09-14 21:48", frm="javier", subject="Cierre lunes 14", business_date="2026-09-14",
         body="""14,9k vs 16 ppto, casi.
115 personas pero solo 7 tickets, eso si buenos (colombianos y americanos).
Una clienta queria el Rosiere negro en 3, no hay.

J."""),

    dict(id="c0915", sent="2026-09-15 21:39", frm="lucia", subject="Cierre MAD01 - 15/09", business_date="2026-09-15",
         body="""Buenas noches,

RESUMEN CIERRE
Venta neta: 24.805 €
Ppto: 15.390 € (+61%)
Tráfico: 102 | Conv.: 13,7%
Tickets: 14 | UPT: 1,5
Comentarios: primer día "de plumas" de la temporada. 2 Arneb negras (a los dos les bajamos una talla, la 4 les quedaba como un saco), 2 Maire blanco roto, 2 cardigan acolchado gris.
Devolución de un cuello alto XL, cambio de opinión.
Sin stock: cuello alto azul marino en L.
Arneb negra ya a cero en 3 y 5.

Lucía"""),

    dict(id="c0916", sent="2026-09-16 21:44", frm="lucia", subject="Cierre MAD01 - 15/09", business_date="2026-09-16",
         body="""Hola,

RESUMEN CIERRE
Venta neta: 18.591 €
Ppto: 16.580 € (+12%)
Tráfico: 118 | Conv.: 8,5%
Comentarios: buen miércoles, muchos mexicanos y americanos.
Lo que nos han pedido y no teníamos: Montgenevre navy 2, Valbourg negro 1, polo blanco M y otra vez el cuello alto azul marino en L (segundo día seguido). ¿Cuándo entra la L en navy? Es de lo que más sale.
Maya verde oliva a cero en 5.

Lucía"""),

    dict(id="c0917", sent="2026-09-17 21:26", frm="lucia", subject="Cierre MAD01 17/09", business_date="2026-09-17",
         body="""Buenas noches,

Día muy malo: 5.480 € contra 20.330 de presupuesto. 107 personas y solo 5 tickets, casi todo gorras.
Envío de hoy recibido sin incidencias, 153 piezas.
Dos devoluciones: cardigan acolchado M por talla y unas Trailgrip mujer 37 (cambio de opinión).

Mañana será otro día.
Lucía"""),

    dict(id="c0918", sent="2026-09-18 21:51", frm="lucia", subject="Cierre MAD01 18/09", business_date="2026-09-18",
         body="""Hola,

Venta 14.790 / ppto 24.050
Tráfico 140, conv 8,6%

Devolución de una Arneb talla 5 por talla: al cliente le quedaba enorme. Ya van varias, la Arneb talla al menos una más grande.
Vendidas 2 bufandas cashmere gris y 2 Tib negros.

Lucía"""),

    dict(id="c0919", sent="2026-09-19 22:24", frm="lucia", subject="Cierre MAD01 - 19/09 sábado", business_date="2026-09-19",
         body="""Buenas noches a todos,

Mejor sábado desde julio.

RESUMEN CIERRE
Venta neta: 36.465 €
Ppto: 33.670 € (+8%)
Tráfico: 214 | Conv.: 7,9%
Tickets: 17 | UPT: 2,0
Comentarios:
4 Maya negros (un señor de Guadalajara se llevó dos para sus hijos, se van a esquiar a Canadá), 4 cardigan logo negro, 3 Montcla negros.
Segunda clienta esta semana que pregunta por el Ambrine marrón chocolate, hoy en talla 2. No tenemos.
También sudadera con capucha negra XS.
Del Maya negro nos quedan pocas tallas después de hoy, he pedido reposición para el envío del jueves 24.

Buen domingo,
Lucía
--
Lucía Fernández Ortega
Store Manager | Moncler Madrid Serrano
Este mensaje es confidencial y va dirigido exclusivamente a sus destinatarios."""),

    dict(id="c0920", sent="2026-09-20 21:15", frm="javier", subject="Cierre domingo 20", business_date="2026-09-20",
         body="""Buenas

19,1k vs 22,7. 136 personas.
Mexicanos y americanos sobre todo. 2 Montgenevre negros.
Me pidieron Hermine blanco roto en 2 y Karakorum negro en 6, ninguno.

Ojo con el Maya negro: queda 1 por talla y en la 1 y la 7 nada. El sabado volaron.

Javi"""),
]

EMAILS += [
    dict(id="c0922", sent="2026-09-22 21:33", frm="lucia", subject="Cierre MAD01 22/09", business_date="2026-09-22",
         body="""Buenas noches,

Venta neta 11.100 € vs 17.890 de ppto (-38%). 106 personas.
Muchos americanos hoy, casi uno de cada cuatro tickets.
Devoluciones: un Tib talla 3 (regalo) y un cambio de Arneb de la 3 a la 2, otra vez por talla grande.
El Maya negro está a cero en talla 3 desde ayer. Si alguien lo pide en 3 no lo tenemos hasta el envío del jueves.
Sin stock también jersey de ochos blanco roto XXL.

Lucía"""),

    dict(id="c0923", sent="2026-09-23 22:02", frm="lucia", subject="Cierre MAD01 23/09", business_date="2026-09-23",
         body="""Hola a todos,

Muy buen miércoles: 26.060 € vs 19.140 (+36%). 122 personas, 12 tickets pero con UPT 2,2.
Bastantes clientes chinos (un grupo de estudiantes con sus padres) y colombianos.
3 sudaderas cuello redondo negras y 2 con capucha negras.

Lo que no tenemos:
- Maire blanco roto talla 4
- Ambrine marrón chocolate talla 2 (ya llevo la cuenta: es la tercera o cuarta en dos semanas)
- Tib navy talla 2
Maya negro ahora también a cero en 4, además de la 3. Tengo dos clientes apuntados esperando el envío de mañana.

Lucía"""),

    dict(id="c0924", sent="2026-09-24 21:40", frm="lucia", subject="Cierre MAD01 24/09", business_date="2026-09-24",
         body="""Buenas noches,

17.910 € vs 22.710 (-21%), 110 personas.

El envío de hoy NO ha llegado. DHL dice "incidencia en el hub", sin más. Es el que trae el Maya negro.

Primer día de Genius Polaris en tienda: una capa negra vendida a una clienta (2.900 €). El resto se la prueba y le queda pequeña, y cuando ve el precio la deja. Veremos.
Hoy nos pidieron el Maya en navy talla 2, tampoco nos queda, y un cardigan acolchado gris L.
Dos mochilas Makaio navy.

Lucía"""),

    dict(id="c0925", sent="2026-09-25 21:58", frm="lucia", subject="Cierre MAD01 25/09", business_date="2026-09-25",
         body="""Hola,

Venta neta 21.205 € / ppto 26.270 (-19%). Tráfico 137, conversión 8,8%.

Seguimos sin el envío del jueves, DHL ahora dice mañana sábado por la mañana.
Muchos mexicanos hoy (más de un 20% de los tickets), casi todos con tax free, compran para irse a la nieve en diciembre. Un cliente de Monterrey quería el Maya negro en 3 y se fue sin nada, le he dicho que mañana.
Sin stock también: Bady negra 4 y Trailgrip mujer negra 40.
3 cuellos altos negros vendidos.

Lucía"""),
]

EMAILS += [
    dict(id="c0925dup", sent="2026-09-25 21:59", frm="lucia", subject="Cierre MAD01 25/09", kind="dup", suffix="_dup",
         body="""Hola,

Venta neta 21.205 € / ppto 26.270 (-19%). Tráfico 137, conversión 8,8%.

Seguimos sin el envío del jueves, DHL ahora dice mañana sábado por la mañana.
Muchos mexicanos hoy (más de un 20% de los tickets), casi todos con tax free, compran para irse a la nieve en diciembre. Un cliente de Monterrey quería el Maya negro en 3 y se fue sin nada, le he dicho que mañana.
Sin stock también: Bady negra 4 y Trailgrip mujer negra 40.
3 cuellos altos negros vendidos.

Lucía"""),

    dict(id="c0926", sent="2026-09-26 22:41", frm="lucia", subject="Cierre MAD01 26/09 + INCIDENCIA ENVÍO (Maya color equivocado)",
         cc=["roberto", "dc"], business_date="2026-09-26",
         attachments=[{"name": "IMG_4471.jpg"}, {"name": "IMG_4472.jpg"}, {"name": "IMG_4473.jpg"}],
         body="""Buenas noches,

Cierre: 26.630 € vs 36.900 de ppto (-28%), 175 personas, 20 tickets.

INCIDENCIA: esta mañana ha llegado por fin el envío del jueves 24 (dos días tarde) y el Maya que pedimos en NEGRO ha llegado todo en AZUL MARINO. 17 piezas, tallas de la 1 a la 7. En el albarán pone negro, en las etiquetas el color es navy. Os adjunto fotos de las etiquetas y de las cajas.

Ya teníamos unos 15 Maya navy en tienda que no rotan, ahora tenemos más de 30. Y el negro sigue a cero en 3 y 4.
Hoy el cliente de Monterrey volvió a por su Maya negro talla 3 y se fue sin nada otra vez. Vendimos 2 navy a clientes a los que el color les daba igual, pero el que viene a por el negro quiere el negro.

He abierto ticket con dc-replenishment (en copia). Necesitamos:
1. recoger los 17 navy
2. que nos manden Maya negro tallas 2 a 5 lo antes posible

Por lo demás, 3 sudaderas con capucha negras y 3 de cuello redondo, 2 gorros. Bastantes mexicanos.

Gracias,
Lucía
--
Lucía Fernández Ortega
Store Manager | Moncler Madrid Serrano
Este mensaje es confidencial y va dirigido exclusivamente a sus destinatarios."""),

    dict(id="re0927rob", sent="2026-09-27 11:42", frm="roberto", to=["lucia"], cc=["ops"], kind="reply",
         reply_to_id="c0926", suffix="_re1", subject="Re: Cierre MAD01 26/09 + INCIDENCIA ENVÍO (Maya color equivocado)",
         body="""Ciao Lucia, grazie per le foto.
Me puedes mandare il numero della spedizione? E quante Maya blu sono llegadas exactamente, por talla?
Domani chiamo CSG. Che desastre.

R.

Inviato da iPhone"""),

    dict(id="c0927", sent="2026-09-27 21:20", frm="javier", subject="cierre dom 27", business_date="2026-09-27",
         body="""Buenas,

26,1k vs 26,4, casi clavado.
Mexicanos y americanos, mucho tax free. 3 Tib negros, 2 Maya verde oliva (al menos el verde se vende).

Tenemos Maire azul marino hasta en la sopa y todo el mundo pidiendo el negro jaja. Hoy le he puesto el navy a un chico en la mano y me ha mirado como si le ofreciera una del Atleti.
Sudadera capucha negra en L tb a cero, me la pidieron.

Lucia lo de Roberto (numero de envio) lo contestas tu mañana vale? yo no lo tengo.
Javi"""),

    dict(id="re0928luc", sent="2026-09-28 10:20", frm="lucia", to=["roberto"], cc=["ops"], kind="reply",
         reply_to_id="re0927rob", suffix="_re2", subject="Re: Cierre MAD01 26/09 + INCIDENCIA ENVÍO (Maya color equivocado)",
         business_date="2026-09-26",
         body="""Hola Roberto,

el número no lo tengo aquí, estoy en casa. Es el envío del jueves 24, que llegó el sábado (DHL). Te lo paso esta tarde desde la tienda si lo necesitas.

Maya navy recibidos en vez de negro, 17 piezas:
talla 1: 1
talla 2: 2
talla 3: 5
talla 4: 4
talla 5: 3
talla 6: 1
talla 7: 1

El albarán dice negro. Del almacén todavía nada, ni acuse de recibo del ticket.
Gracias por llamarles.

Lucía

Enviado desde mi iPhone"""),

    dict(id="c0928", sent="2026-09-28 21:45", frm="javier", subject="cierre lunes 28", business_date="2026-09-28",
         body="""lunes raro: 23,9k vs 20 de ppto, +19%!
104 personas y 14 tickets. Españoles sobre todo, algun mexicano y un par de argentinos.
3 gorros negros, 2 cardigan logo negro, 2 Maire navy (esas si, de mujer, se venden bien).

Maya negro en 3 y 4 todavia a cero. El navy no lo quiere nadie.

J."""),

    dict(id="c0929", sent="2026-09-29 21:37", frm="lucia", subject="Cierre MAD01 29/09", business_date="2026-09-29",
         body="""Buenas noches,

Venta 27.481 € vs 20.170 (+36%). Tráfico 120, conversión 11,7%.
Mexicanos y chinos sobre todo. 3 Rosiere negros, 2 Hermine navy, 2 Montcla navy.

Devolución de un chaleco Tib negro talla 3: el tirador de la cremallera se sale, el cliente casi lo pierde en la calle. Es el primero que vemos así, lo aparto para calidad con foto.

Sin stock: Hermine navy 3, cardigan logo navy XXL, sudadera capucha negra L.

Del almacén sobre el Maya ni respuesta.

Lucía"""),

    dict(id="c0930", sent="2026-09-30 22:06", frm="lucia", subject="Cierre MAD01 30/09", business_date="2026-09-30",
         body="""Hola a todos,

21.675 € vs 22.170 (-2%), 129 personas, 15 tickets.

Tib: dos devoluciones más con el mismo problema del tirador de la cremallera (tallas 3 y 4). Ya son tres en dos días. ¿Sabemos algo de un lote defectuoso? Me preocupa porque el Tib se vende mucho y vamos a tener más.

Polaris: hoy 2 capas negras a clientes chinos, las primeras que se venden "bien". El cliente europeo sigue sin entenderla.

Lo que nos han pedido sin stock:
- Maya negro talla 4 (y seguimos sin respuesta del almacén, cuatro días)
- Rosiere negro 3 y 5
- cuello alto negro M
- Trailgrip GTX negras 45
- una chica asiática enseñando en el móvil la foto del Ilvaro rosa talla 0, no lo hemos tenido nunca
Devolución de un Maya verde oliva talla 5 por talla.

Lucía"""),

    dict(id="c1001", sent="2026-10-01 21:55", frm="lucia", subject="Cierre MAD01 01/10", business_date="2026-10-01",
         attachments=[{"name": "IMG_4502.jpg"}],
         body="""Buenas noches,

Venta 11.000 € vs 24.460 (-55%). Día malo.

1) El envío de hoy ha llegado a su hora... y OTRA VEZ el Maya viene en azul marino en lugar de negro. 20 piezas más. Foto de las etiquetas adjunta. Tenemos ya unos 50 Maya navy en la tienda y cero negros en 3 y 4. No sé qué está pasando en el almacén pero alguien tiene que mirarlo.
2) El contador de la puerta marca 0 desde esta mañana. Imagino que se ha colgado, mañana llamo a IT. Hoy no tengo tráfico ni conversión.
3) Dos devoluciones más del Tib por la cremallera (tallas 4 y 5). Van cinco.

Vendidos 3 Karakorum negros. Sin stock: Flammette negra 3 y cuello alto navy S.

Lucía"""),

    dict(id="c1002", sent="2026-10-02 21:49", frm="lucia", subject="Cierre MAD01 02/10", business_date="2026-10-02",
         cc=["roberto", "it"],
         body="""Hola,

RESUMEN CIERRE
Venta neta: 27.610 €
Ppto: 29.190 € (-5%)
Tráfico: 0 (contador roto) - estimado a mano unas 150 personas
Conv.: aprox. 11%
Tickets: 16
Comentarios:
- Contador: sigue marcando cero. Ticket abierto con it-helpdesk esta mañana, en copia. Mientras, contamos a ojo desde caja, no es exacto.
- Maya: segundo email al almacén, nada. Hoy vendimos 2 navy, algo es algo.
- 2 Bady negras, 2 Karakorum negros. Americanos y mexicanos.
- Una devolución de Hermine talla 1, cambio de opinión.

Lucía"""),
]

EMAILS += [
    dict(id="c1004", sent="2026-10-04 21:30", frm="javier", subject="cierre finde 3-4/10", business_date="2026-10-03,2026-10-04",
         body="""Buenas!

Os mando el finde junto, ayer Lucia salio tarde y no le dio tiempo.

Sabado: 26,3k vs 41,5 de ppto (-37%). Flojo para ser sabado.
Domingo: 34,9k vs 27,1 (+29%). Domingazo.

El contador sigue muerto, a ojo el sabado entrarian unas 250 personas y hoy unas 200. Conversion ni idea.

Hoy 5 Montgenevre negros, una familia mexicana q se va a esquiar a Colorado en navidad. Tb 3 cardigan logo negro y 3 sudaderas capucha gris.
Maya negro: hoy me lo han pedido en 1, 2 y 3. Ya esta a cero en 2, 3, 4 y 5. Navy tenemos para vestir a medio Madrid.
Ambrine marron chocolate talla 0, dos clientas distintas. Nada.
El sabado tb pidieron Flammette negra 3 y Maya negro 3.

Devolucion de un Karakorum talla 3, cambio de opinion.

Javi

Enviado desde mi iPhone"""),

    dict(id="c1005", sent="2026-10-05 21:40", frm="javier", to=["opsit"], subject="cierre lunes 05/10", business_date="2026-10-05",
         body="""Buenas,

14,1k vs 21,9 ppto.
Conversion: 0% jaja, el contador sigue roto. A ojo unas 110 personas.
Muchos americanos hoy.

Sin stock: Rosiere negra 4, Peyre negro 1, sudadera capucha navy L, camiseta logo blanca L.
2 Bady negras.

J."""),

    dict(id="re1006rob", sent="2026-10-06 08:52", frm="roberto", to=["javier"], cc=["lucia"], kind="reply",
         reply_to_id="c1005", suffix="_re1", subject="Re: cierre lunes 05/10",
         body="""Javi, l'hai mandata a retail-ops-italy :) Mandala anche a ops Spain por favor.

Altra cosa: nel report vedo visitors 0 desde el jueves y la conversion vacía. Il contapersone está roto? Quando lo arreglan?

R."""),

    dict(id="re1006luc", sent="2026-10-06 13:15", frm="lucia", to=["roberto"], cc=["ops", "javier", "it"], kind="reply",
         reply_to_id="re1006rob", suffix="_re2", subject="Re: cierre lunes 05/10",
         body="""Hola Roberto,

sí, el contador está roto desde el jueves 1, marca cero todo el día. Ticket abierto con it-helpdesk el viernes 2, nos dicen que el técnico viene el jueves 8 por la mañana.

Mientras tanto contamos a mano desde caja, muy aproximado:
jueves 1: ~90
viernes 2: ~150
sábado 3: ~250
domingo 4: ~200
lunes 5: ~110

La conversión de esta semana mejor no mirarla. La venta y los tickets sí son buenos.

Lucía"""),

    dict(id="c1006", sent="2026-10-06 21:58", frm="javier", subject="cierre martes 6", business_date="2026-10-06",
         body="""Buenas (esta vez a la lista buena jaja)

24,4k vs 22,1, +11%. Contador roto, a ojo unas 130 personas.
2 Ilvaro blanco roto, 2 cuellos altos negros, un Valbourg.

El Maya negro hoy me lo han pedido TRES clientes, en 1, 3 y 4. Uno de Mexico con la foto en el movil. Les he enseñado el navy y nada, ni caso.
Tb sin stock Karakorum negro 6 y camiseta blanca L (otra vez).
Devolucion de una Arneb talla 3, cambio de opinion.

Javi"""),

    dict(id="fwd1007dc", sent="2026-10-07 11:05", frm="lucia", cc=["roberto", "javier"], kind="fwd", suffix="_fwd",
         subject="RV: RE: MAYA colore sbagliato / wrong colour - MAD01 Serrano",
         body="""Os reenvío la respuesta del almacén sobre el Maya, llegó ayer a las 18:30. Diez días después del primer ticket.

Lo importante: confirman error de picking en los dos envíos, el negro salió ayer y debería llegar el jueves 8. Los navy NO los devolvemos hasta que nos manden instrucciones (RMA).

Lucía

-----Mensaje original-----
De: DC Replenishment CSG <dc-replenishment@moncler-retail.example>
Enviado el: martes, 6 de octubre de 2026 18:27
Para: Lucía Fernández Ortega <lucia.fernandez@moncler-retail.example>
CC: Roberto Galli <roberto.galli@moncler-retail.example>
Asunto: RE: MAYA colore sbagliato / wrong colour - MAD01 Serrano

Hi Lucía,

sorry for the late answer, high volumes this week.
We checked shipments SHP02600337 (arrived 26/09) and SHP02600382 (arrived 01/10): picking error confirmed, MAYA navy picked instead of MAYA black, same size breakdown (17 + 20 pcs).
Black MAYA has been added to your next replenishment, departure 06/10, ETA store 08/10.
For the navy pieces please keep them in stock for now, RMA instructions will follow.

Best regards
Replenishment Team
Castel San Giovanni DC"""),

    dict(id="c1007", sent="2026-10-07 21:43", frm="lucia", subject="Cierre MAD01 07/10", business_date="2026-10-07",
         body="""Buenas noches,

Venta neta 18.720 € vs 24.250 (-23%). Contador todavía roto, calculo unas 140 personas.
Mexicanos y colombianos, algún chino.

Sin stock hoy:
- Maya negro talla 2, dos clientes (uno de ellos el de Monterrey, que ya ha venido tres veces)
- Maire negra 1
- Montgenevre negro 4
- Tib negro 3 (las devoluciones por la cremallera nos han dejado sin la 3)
- Polaris capa negra en S (para su hija, muy menuda, y la S no nos ha llegado)
- sudadera cuello redondo negra S

Según el almacén el Maya negro llega mañana. El técnico del contador también viene mañana. Crucemos los dedos.

Lucía
--
Lucía Fernández Ortega
Store Manager | Moncler Madrid Serrano
Este mensaje es confidencial y va dirigido exclusivamente a sus destinatarios."""),

    dict(id="c1008", sent="2026-10-08 21:36", frm="lucia", subject="Cierre MAD01 08/10", business_date="2026-10-08",
         body="""Hola,

Buenas y malas noticias.

La buena: el técnico vino a las 10, cambió el sensor de la puerta y el contador vuelve a contar. Hoy 155 personas, conversión 11,6%. Venta 26.680 € vs 28.230 (-6%).
La mala: el envío de hoy (el que traía el Maya negro) no ha llegado. DHL: "retraso".

Vendidos 3 Maya navy (los tres a gente que no tenía preferencia de color, con un poco de insistencia) y 4 sudaderas cuello redondo negras.
Sin stock: cardigan logo negro XS y cuello redondo negra S.

Lucía"""),

    dict(id="c1009", sent="2026-10-09 21:57", frm="lucia", subject="Cierre MAD01 09/10", business_date="2026-10-09",
         body="""Buenas noches,

23.840 € vs 31.880 (-25%). 199 personas, conversión 6,5%. Empieza el puente del Pilar y Serrano está lleno de gente paseando, pero se compra poco.
Bastantes mexicanos.
2 Montcla negros, 2 Arneb negras (las dos una talla menos de la que pedían), 2 cardigan logo negro.

Sin stock: Maya negro talla 3 (otra vez) y cuello redondo negra L.
El envío sigue sin llegar. Ahora DHL dice domingo. En domingo, sí.

Lucía"""),

    dict(id="c1010", sent="2026-10-10 22:35", frm="lucia", subject="Cierre MAD01 10/10 sábado", business_date="2026-10-10",
         body="""Buenas noches a todos,

Sábado de puente:
Venta neta 39.210 € (ppto 44.740, -12%)
Tráfico 301 (no recuerdo un sábado así), conversión 7,3%
Tickets 22

Mucho cliente latinoamericano por el puente de la Hispanidad: mexicanos, americanos de Miami, colombianos. Cola en caja por el tax free toda la tarde. Una clienta de Barranquilla me dijo que en Miami el Maya le sale más barato; con la devolución del IVA aquí se le queda casi igual y se lo llevó (navy, porque negro no hay).
3 Maya navy, 3 Bady negras, 3 sudaderas capucha gris.

Lista de lo que no teníamos (larga):
Maire negra 0
Bady negra 3
Flammette negra 3
Ambrine marrón chocolate 1
Montgenevre negro 1
sudadera capucha navy S y L

Mañana llega (dicen) el envío con el Maya negro.

Lucía"""),

    dict(id="c1011", sent="2026-10-11 21:25", frm="javier", subject="cierre domingo 11 - LLEGO EL MAYA NEGRO", business_date="2026-10-11",
         body="""Buenas!!

El envio del jueves ha llegado hoy domingo a mediodia (3 dias tarde) y esta vez SI trae Maya negro: unas 20 piezas, tallas 2 a 7 (en la 1 nada). Lo hemos colgado en 10 minutos y han caido 3 en la tarde. Lucia, he escrito yo a los de la lista de espera.

28,8k vs 31,4. 171 personas, conversion 13%.
3 Tib negros, 3 Montcla navy.

Dia de devoluciones (5): Arneb de la 5 a la 4 por talla (la de siempre), Karakorum 4 por talla, una Bady rosa talla 0, un Montcla 3 y un gorro.
Sin stock: Ambrine chocolate 2, Arneb negra 4 (se fue con el cambio jaja), cardigan logo negro XS, sudadera capucha gris M.

Navy: seguimos con 40 y pico Maya navy en almacen. Del RMA ni noticias.

Javi

Enviado desde mi iPhone"""),

    dict(id="c1012", sent="2026-10-12 21:20", frm="store", subject="Cierre Serrano 12/10 (feriado)", business_date="2026-10-12",
         body="""Hola a todos!

Les escribo yo, Martina, Javi y Lucía libran por el feriado.

Venta 14.410 €, presupuesto 23.140. Contador 125 personas.
A la mañana estaba todo cortado por el desfile por Colón y la Castellana, hasta la 1 no entró casi nadie. A la tarde mejor, turistas chinos y colombianos.
Vendimos 2 Montgenevre negros, una gorra y unos guantes.
Dos devoluciones chiquitas: una gorra por talla y una riñonera Légère (cambió de idea).

Ahora que tenemos Maya negro por fin lo puedo ofrecer! Un chico de Bogotá se lo probó en 4, le quedaba perfecto, se lo va a pensar y vuelve antes de irse el jueves.

Saludos!
Martina E."""),
]

EMAILS += [
    dict(id="c1013", sent="2026-10-14 09:48", frm="javier", subject="cierre martes 13 (perdon, ayer se me paso)",
         business_date="2026-10-13",
         body="""Buenos dias, anoche sali corriendo y no lo mande, perdon.

Martes 13: 16,5k vs 21,6 de ppto. 137 personas, 9 tickets.
Americanos y algun argentino. 2 camisetas negras, un Peyre, una riñonera.
Solo una peticion sin stock: Ilvaro blanco roto talla 2.
El chico de Bogota no volvio a por el Maya negro, una pena.

Javi"""),

    dict(id="c1014", sent="2026-10-14 21:41", frm="lucia", subject="Cierre MAD01 14/10", business_date="2026-10-14",
         body="""Buenas noches,

21.220 € vs 24.530 (-14%). 131 personas, conversión 11,5%.
Por fin se nota algo de fresco por las mañanas: 3 bufandas de cashmere negras, 2 Montgenevre negros, 2 Bady negras.

Sin stock: Montgenevre negro 2, Trailgrip mujer blanco roto 40, Insolux negro 40.
La Maire negra está a cero en 0, 1 y 2. Merch nos dice que vuelve a haber en el almacén a partir del 16, ¿nos podéis confirmar que Madrid está en el reparto? La piden mucho.

Lucía"""),

    dict(id="c1015", sent="2026-10-15 21:30", frm="lucia", subject="cierre 15/10", business_date="2026-10-15",
         body="""Hola,

30.125 € vs 29.200, +3%. Primer día en presupuesto en mucho tiempo. 186 personas, 21 tickets.

Envío de hoy a su hora, 183 piezas, todo correcto (lo he revisado caja por caja, ya me fío poco). Más Maya negro, ahora vamos bien de tallas.
Ambrine marrón: nos mandan UNA talla 00, que no la pide nadie. La 0, la 1 y la 2 siguen sin llegar.
La Maire negra no venía.

3 gorros blancos, 3 pares de guantes técnicos negros.

Lucía"""),

    dict(id="fwd1016cli", sent="2026-10-16 13:10", frm="martina", cc=["lucia", "merch"], kind="fwd", suffix="_fwd",
         subject="RV: abrigo Ambrine chocolate talla 1", business_date="2026-10-16",
         body="""Hola! Les reenvío el mail de una clienta colombiana de mi client book. Necesita el Ambrine marrón chocolate en talla 1 antes del sábado 24 que se vuelve a Bogotá. Acá no queda ninguna en 0, 1 o 2.
¿Alguna tienda tiene para hacer transfer? Milán, París, la que sea. Es una clienta re buena, el año pasado se llevó tres piezas.

Gracias!
Martina

---------- Mensaje reenviado ----------
De: Catalina R. <cata.restrepo@mail.example>
Fecha: jue, 15 oct 2026 a las 23:02
Asunto: abrigo
Para: Martina Echeverría <martina.echeverria@moncler-retail.example>

Hola Martina, ¿cómo estás?
Te escribo por el abrigo largo marrón que vimos el domingo pasado, el que tiene cinturón. No me puedo sacar de la cabeza ese color!! ¿Me lo puedes conseguir en talla 1? Me devuelvo a Bogotá el 24 y quiero llevármelo para el viaje a Europa en diciembre.
El negro ya lo tengo de otra marca, así que solo me interesa el marrón.
Mil gracias, un abrazo
Cata"""),

    dict(id="c1016", sent="2026-10-16 22:04", frm="lucia", subject="Cierre MAD01 16/10", business_date="2026-10-16",
         body="""Buenas noches,

Venta neta 35.920 € vs 36.120 (-1%). Tráfico 171, conversión 13,4%.
Muy buen viernes. Mexicanos sobre todo (casi 1 de cada 5 tickets). 3 Trailgrip mujer negras, 3 cardigan logo negro, 3 Montcla navy.

Sin stock:
- Maire negra 2
- Ambrine chocolate 1 (la clienta de Martina, ver su correo)
- Peyre negro 6
- Trailgrip mujer negra 37

Lucía"""),

    dict(id="c1017", sent="2026-10-17 22:30", frm="lucia", subject="Cierre MAD01 17/10 - sábado", business_date="2026-10-17",
         body="""Buenas noches a todos,

¡Por fin un sábado en presupuesto!
Venta neta: 45.070 € (ppto 44.940)
Tráfico: 270 | Conv.: 9,3%
Tickets: 25 | UPT: 1,7

3 Flammette negras, 3 Tib negros (crucemos los dedos con las cremalleras), 3 Maire beige.
La Maire negra la han pedido hoy en 1 y en 2, seguimos a cero. Algunas clientas se van a la beige, otras no.
Una devolución de Montcla talla 5 por talla.

Gracias al equipo, día durísimo.
Lucía
--
Lucía Fernández Ortega
Store Manager | Moncler Madrid Serrano
Este mensaje es confidencial y va dirigido exclusivamente a sus destinatarios."""),

    dict(id="re1018rob", sent="2026-10-18 10:05", frm="roberto", to=["lucia"], cc=["ops", "javier"], kind="reply",
         reply_to_id="c1017", suffix="_re1", subject="Re: Cierre MAD01 17/10 - sábado",
         body="""Brava Lucia y todo el equipo! Finalmente un sabado en presupuesto, era ora.
Per la Maire negra ho chiesto a merch, mi dicen que el reparto sale la semana prossima. Ti aggiorno.

Roberto

Inviato da iPhone"""),

    dict(id="c1018", sent="2026-10-18 21:10", frm="martina", subject="Cierre domingo 18/10", business_date="2026-10-18",
         body="""Hola a todos,

Domingo: 21.440 € vs 31.960 de presupuesto. 171 personas por el contador.
Hoy muchísimos mexicanos, casi un tercio de los tickets, y americanos.

Lo lindo del día: vino un cliente de Guadalajara que se había llevado el Maya azul marino en talla 3 hace unas semanas porque no había negro. Lo devolvió (motivo color) y se llevó el negro en la misma talla, feliz. Vendimos 2 Maya negros en total.
También una Polaris oversize negra, a un cliente americano altísimo, la única talla que le entraba jaja.

Sin stock: Maire beige 00 e Ilvaro negro talla 0.
Devolución de un jersey de ochos M por talla.

Martina"""),

    dict(id="c1019", sent="2026-10-19 21:39", frm="javier", subject="cierre lunes 19", business_date="2026-10-19",
         body="""Buenas,

19,4k vs 24,8 ppto. 136 personas.
Españoles casi todos, algun mexicano y colombiano.
2 Hermine blanco roto y... una capa Polaris blanca!! milagro. La señora ni pregunto el precio.

Sin stock: Maire negra 1 (otra vez) y Montgenevre navy 2.
Devoluciones: Rosiere talla 3 por talla y un cardigan acolchado S, la clienta dice q le salen bolitas.

J."""),

    dict(id="c1020", sent="2026-10-20 21:24", frm="lucia", subject="cierre 20/10", business_date="2026-10-20",
         body="""Hola,

Día malísimo: 7.430 € vs 24.230. 124 personas y 6 tickets. No tengo explicación, entra gente, mira y se va.
Ambrine chocolate talla 0, otra clienta. Polaris capa blanca en L, no hay.

Lucía"""),

    dict(id="c1021", sent="2026-10-21 21:52", frm="lucia", subject="Cierre MAD01 21/10", business_date="2026-10-21",
         body="""Buenas noches,

25.730 € vs 25.860, prácticamente en presupuesto. 172 personas, 15 tickets.
3 cardigan logo negro, 2 Maya verde oliva, 2 Bady rosa.

Sin stock: Hermine blanco roto 2 y Flammette negra 3. La Flammette negra en 3 nos la han pedido ya cuatro veces este mes.
Otra devolución de Tib, esta vez navy talla 2, por calidad.

Pendientes:
- Maire negra: sigue sin llegar
- Maya navy: seguimos con unos 40 en tienda, sin instrucciones de devolución
- Ambrine chocolate 0-1-2: nada

Lucía"""),
]
