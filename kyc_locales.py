# Native-language copy and fallback question packs for PlotTwist.
# Canonical topic keys remain Hebrew internally so multilingual support does not
# require a risky migration of existing rooms/history.

SUPPORTED_LANGUAGES = {
    'en': {'name': 'English', 'dir': 'ltr'},
    'es': {'name': 'Español', 'dir': 'ltr'},
    'pt-BR': {'name': 'Português (Brasil)', 'dir': 'ltr'},
    'fr': {'name': 'Français', 'dir': 'ltr'},
    'ja': {'name': '日本語', 'dir': 'ltr'},
    'he': {'name': 'עברית', 'dir': 'rtl'},
}

TOPIC_LABELS = {
 'מה היית עושה אם…': {'en':'What would you do if…','es':'¿Qué harías si…?','pt-BR':'O que você faria se…','fr':'Tu ferais quoi si…','ar':'ماذا ستفعل لو…','he':'מה היית עושה אם…'},
 'דילמות': {'en':'Dilemmas','es':'Dilemas','pt-BR':'Dilemas','fr':'Dilemmes','ar':'مواقف وحيرة','he':'דילמות'},
 'מי הכי…': {'en':'Who’s most likely…','es':'¿Quién es más probable que…?','pt-BR':'Quem é mais provável…','fr':'Qui est le plus susceptible…','ar':'مين الأكثر احتمالاً…','he':'מי הכי…'},
 'מביך אבל מצחיק': {'en':'Awkward but funny','es':'Incómodo pero gracioso','pt-BR':'Vergonhoso, mas engraçado','fr':'Gênant mais drôle','ar':'محرج بس مضحك','he':'מביך אבל מצחיק'},
 'סודות והרגלים': {'en':'Secrets & habits','es':'Secretos y hábitos','pt-BR':'Segredos e hábitos','fr':'Secrets et habitudes','ar':'أسرار وعادات','he':'סודות והרגלים'},
 'משפחה': {'en':'Family','es':'Familia','pt-BR':'Família','fr':'Famille','ar':'العائلة','he':'משפחה'},
 'חברות ואמון': {'en':'Friendship & trust','es':'Amistad y confianza','pt-BR':'Amizade e confiança','fr':'Amitié et confiance','ar':'الصداقة والثقة','he':'חברות ואמון'},
 'דייטים': {'en':'Dating','es':'Citas','pt-BR':'Encontros','fr':'Dating','ar':'المواعدة','he':'דייטים'},
 'טיולים וחופשות': {'en':'Travel & vacations','es':'Viajes y vacaciones','pt-BR':'Viagens e férias','fr':'Voyages et vacances','ar':'السفر والإجازات','he':'טיולים וחופשות'},
 'כסף מטורף': {'en':'Crazy money','es':'Dinero loco','pt-BR':'Dinheiro sem noção','fr':'Argent fou','ar':'فلوس بلا حدود','he':'כסף מטורף'},
 'חלומות ופנטזיות': {'en':'Dreams & fantasies','es':'Sueños y fantasías','pt-BR':'Sonhos e fantasias','fr':'Rêves et fantasmes','ar':'أحلام وخيالات','he':'חלומות ופנטזיות'},
 'גייז / LGBTQ+': {'en':'LGBTQ+','es':'LGBTQ+','pt-BR':'LGBTQ+','fr':'LGBTQ+','ar':'LGBTQ+','he':'גייז / LGBTQ+'},
 'זוגיות': {'en':'Relationships','es':'Relaciones','pt-BR':'Relacionamentos','fr':'Relations','ar':'العلاقات','he':'זוגיות'},
 'חיי לילה': {'en':'Nightlife','es':'Vida nocturna','pt-BR':'Vida noturna','fr':'Vie nocturne','ar':'السهر والحياة الليلية','he':'חיי לילה'},
 'נסיעות': {'en':'Travel','es':'Viajes','pt-BR':'Viagens','fr':'Voyages','ar':'السفر','he':'נסיעות'},
 'כסף': {'en':'Money','es':'Dinero','pt-BR':'Dinheiro','fr':'Argent','ar':'المال','he':'כסף'},
 'קריירה ועסקים': {'en':'Career & business','es':'Carrera y negocios','pt-BR':'Carreira e negócios','fr':'Carrière et business','ar':'العمل والبيزنس','he':'קריירה ועסקים'},
 'רשתות חברתיות': {'en':'Social media','es':'Redes sociales','pt-BR':'Redes sociais','fr':'Réseaux sociaux','ar':'السوشيال ميديا','he':'רשתות חברתיות'},
 'נוסטלגיה': {'en':'Nostalgia','es':'Nostalgia','pt-BR':'Nostalgia','fr':'Nostalgie','ar':'النوستالجيا','he':'נוסטלגיה'},
 'אוכל': {'en':'Food','es':'Comida','pt-BR':'Comida','fr':'Food','ar':'الأكل','he':'אוכל'},
 'מוזיקה': {'en':'Music','es':'Música','pt-BR':'Música','fr':'Musique','ar':'الموسيقى','he':'מוזיקה'},
 'הרפתקאות': {'en':'Adventures','es':'Aventuras','pt-BR':'Aventuras','fr':'Aventures','ar':'مغامرات','he':'הרפתקאות'},
 'אישיות': {'en':'Personality','es':'Personalidad','pt-BR':'Personalidade','fr':'Personnalité','ar':'الشخصية','he':'אישיות'},
 'טכנולוגיה': {'en':'Technology','es':'Tecnología','pt-BR':'Tecnologia','fr':'Technologie','ar':'التكنولوجيا','he':'טכנולוגיה'},
 'ספורט וכושר': {'en':'Sports & fitness','es':'Deporte y fitness','pt-BR':'Esporte e fitness','fr':'Sport et fitness','ar':'الرياضة واللياقة','he':'ספורט וכושר'},
 'תרבות ופופ': {'en':'Pop culture','es':'Cultura pop','pt-BR':'Cultura pop','fr':'Culture pop','ar':'البوب والثقافة','he':'תרבות ופופ'},
 'אינטימיות למבוגרים': {'en':'Adult / Intimacy (18+)','es':'Adultos / Intimidad (18+)','pt-BR':'Adulto / Intimidade (18+)','fr':'Adulte / Intimité (18+)','ar':'للبالغين / حميمية (+18)','he':'אינטימיות למבוגרים'},
}

OTHER_LABELS = {
 'en':'✏️ Something else', 'es':'✏️ Otra cosa', 'pt-BR':'✏️ Outra coisa',
 'fr':'✏️ Autre chose', 'ja':'✏️ その他', 'ar':'✏️ شيء آخر', 'he':'✏️ משהו אחר'
}

def normalize_language(value):
    raw = str(value or '').strip()
    aliases = {'pt':'pt-BR','pt_br':'pt-BR','pt-br':'pt-BR','en-US':'en','en-GB':'en','es-ES':'es','fr-FR':'fr','ja-JP':'ja','he-IL':'he'}
    raw = aliases.get(raw, raw)
    return raw if raw in SUPPORTED_LANGUAGES else 'en'

def direction(lang):
    return SUPPORTED_LANGUAGES[normalize_language(lang)]['dir']

JA_TOPIC_LABELS = {
 'מה היית עושה אם…':'もし〜だったら？','דילמות':'究極の選択','מי הכי…':'一番〜しそうなのは？','מביך אבל מצחיק':'恥ずかしいけど笑える',
 'סודות והרגלים':'秘密とクセ','משפחה':'家族','חברות ואמון':'友情と信頼','דייטים':'デート','טיולים וחופשות':'旅行・バカンス',
 'כסף מטורף':'もし大金があったら','חלומות ופנטזיות':'夢と妄想','גייז / LGBTQ+':'LGBTQ+','זוגיות':'恋愛・パートナー',
 'חיי לילה':'ナイトライフ','נסיעות':'旅行','כסף':'お金','קריירה ועסקים':'仕事・ビジネス','רשתות חברתיות':'SNS',
 'נוסטלגיה':'懐かしネタ','אוכל':'食べ物','מוזיקה':'音楽','הרפתקאות':'冒険','אישיות':'性格','טכנולוגיה':'テクノロジー',
 'ספורט וכושר':'スポーツ・フィットネス','תרבות ופופ':'ポップカルチャー','אינטימיות למבוגרים':'大人・親密な話（18+）'
}

def topic_label(topic, lang):
    lang = normalize_language(lang)
    if lang == 'ja': return JA_TOPIC_LABELS.get(topic, topic)
    return TOPIC_LABELS.get(topic, {}).get(lang, topic)

def topic_labels(topics, lang):
    return [topic_label(t, lang) for t in topics or []]

def other_label(lang):
    return OTHER_LABELS[normalize_language(lang)]

# These packs are written independently in each language rather than translated at
# request time. They are the no-AI fallback and intentionally sound conversational.
GENERAL_BY_LANG = {
'en':[
 ('know','{s} suddenly gets tomorrow completely free. What happens first?',['Sleeps in','Books something spontaneous','Makes plans with friends','Finally does the thing they keep postponing']),
 ('know','{s} walks into a restaurant with a huge menu. How do they pick?',['The weirdest thing','The safe favorite','Asks the waiter','Orders a bit of everything']),
 ('know','{s} finds a ridiculously cheap flight leaving tonight. What do they do?',['Book it immediately','Research for an hour','Send it to the group chat','Decide it is too chaotic']),
 ('know','Someone cancels on {s} at the last minute for the third time. What is the reaction?',['Says it straight','Gives one more chance','Pulls back from the friendship','Jokes about it but remembers']),
 ('know','{s} gets $1,000 that must be spent only on fun. Where does it go?',['A weekend away','Shopping','A great dinner for everyone','Something they have wanted forever']),
 ('know','{s} is running late. What is most likely happening?',['Still choosing clothes','Looking for keys','Saying “two minutes” from home','Actually already on the way']),
 ('know','{s} receives a message that says “We need to talk.” First thought?',['What did I do?','This is drama','Calls immediately','Pretends not to have seen it yet']),
 ('know','{s} has to give up one app for a month. Which one goes first?',['Instagram','TikTok','Dating apps','Food delivery']),
 ('know','A song {s} loves comes on in public. What happens?',['Sings with no shame','Tiny dance','Just smiles','Records it for the group']),
 ('know','{s} has to plan a perfect lazy Sunday. What wins?',['Bed and streaming','Beach or park','Long meal with friends','A totally unplanned day']),
 ('know','{s} gets a brand-new phone. What do they do first?',['Move everything over','Test the camera','Organize the apps','Leave setup for later']),
 ('know','The group plan falls apart an hour before. What role does {s} take?',['Fixes the plan','Enjoys the chaos','Gets annoyed','Turns it into a joke']),
 ('know','{s} can live anywhere for six months, rent paid. What matters most?',['Beach','Big city','Nature','Being close to people they love']),
 ('know','{s} is offered a scary-but-safe activity on vacation. What is the answer?',['Absolutely yes','Needs convincing','Only if everyone does it','No chance']),
 ('know','{s} posts a story and regrets it two minutes later. What happens?',['Deletes it','Leaves it up','Checks who already saw it','Asks a friend if it was cringe']),
 ('know','{s} gets an unexpected compliment from a stranger. How do they react?',['Owns it','Gets shy','Makes a joke','Thinks about it all day']),
 ('know','{s} has to choose one thing to be free forever. What do they pick?',['Flights','Restaurants','Rent','Concerts']),
 ('know','{s} gets stuck at an airport for eight hours. What is their survival plan?',['Find a lounge','Explore the city','Complain dramatically','Sleep anywhere']),
 ('know','{s} is handed the aux cable for a road trip. What is the vibe?',['Crowd-pleasers','Their own niche playlist','Throwback hits','Lets someone else handle it']),
 ('know','{s} has one hour with zero responsibilities and zero notifications. What do they do?',['Nap','Go for a walk','Watch something','Call someone']),
 ('know','{s} has to host dinner with almost no notice. What happens?',['Cooks properly','Orders everything','Turns it into snacks and drinks','Panics, then somehow nails it']),
 ('know','{s} can instantly become great at one thing. What sounds best?',['A language','Cooking','Music','Business']),
 ('room','Who here would {s} trust most to plan a surprise without ruining it?',[]),
 ('room','Who here is most likely to make {s} laugh at the worst possible moment?',[]),
 ('room','Who here would {s} call first if they needed a brutally honest opinion?',[]),
 ('room','Who here would {s} most happily get stuck with on a 12-hour trip?',[]),
],
'es':[
 ('know','A {s} le regalan todo el día de mañana sin obligaciones. ¿Qué hace primero?',['Duerme hasta tarde','Reserva algo improvisado','Monta plan con amigos','Hace por fin eso que lleva semanas posponiendo']),
 ('know','{s} entra a un restaurante con una carta eterna. ¿Cómo elige?',['Lo más raro','Su apuesta segura','Pregunta al camarero','Pide para compartir']),
 ('know','{s} encuentra un vuelo absurdamente barato que sale esta noche. ¿Qué hace?',['Lo compra ya','Investiga una hora','Lo manda al grupo','Decide que es demasiado caos']),
 ('know','Un amigo cancela a {s} por tercera vez a última hora. ¿Reacción?',['Se lo dice de frente','Le da otra oportunidad','Toma distancia','Se ríe, pero se acuerda']),
 ('know','A {s} le caen 1.000 € que solo puede gastar en diversión. ¿Dónde van?',['Escapada','Compras','Cena increíble para todos','Algo que lleva tiempo queriendo']),
 ('know','{s} va tarde. ¿Qué está pasando de verdad?',['Sigue eligiendo ropa','Busca las llaves','Dice “dos minutos” desde casa','Ya está de camino']),
 ('know','A {s} le llega “tenemos que hablar”. ¿Primer pensamiento?',['¿Qué hice?','Se viene drama','Llama al instante','Hace como que no lo vio']),
 ('know','{s} tiene que borrar una app durante un mes. ¿Cuál cae?',['Instagram','TikTok','Apps de citas','Delivery']),
 ('know','Suena una canción que {s} ama en público. ¿Qué pasa?',['Canta sin vergüenza','Baila un poco','Solo sonríe','La graba para el grupo']),
 ('know','Domingo perfecto y cero planes para {s}. ¿Qué gana?',['Cama y series','Playa o parque','Comida larga con amigos','Improvisar todo']),
 ('know','{s} estrena móvil. ¿Qué hace primero?',['Pasa todos los datos','Prueba la cámara','Ordena las apps','Lo configura más tarde']),
 ('know','El plan del grupo se cae una hora antes. ¿Qué papel toma {s}?',['Salva el plan','Disfruta el caos','Se enfada','Lo convierte en chiste']),
 ('know','{s} puede vivir seis meses donde quiera con el alquiler pagado. ¿Qué pesa más?',['Playa','Gran ciudad','Naturaleza','Estar cerca de su gente']),
 ('know','En vacaciones le ofrecen a {s} una actividad que da miedo pero es segura. ¿Qué dice?',['Voy de una','Hay que convencerle','Solo si van todos','Ni loco/a']),
 ('know','{s} sube una story y se arrepiente a los dos minutos. ¿Qué hace?',['La borra','La deja','Mira quién ya la vio','Pregunta a un amigo si dio cringe']),
 ('know','Un desconocido le suelta un cumplido inesperado a {s}. ¿Reacción?',['Se lo cree y lo disfruta','Se pone tímido/a','Hace una broma','Le da vueltas todo el día']),
 ('know','{s} puede conseguir una cosa gratis para siempre. ¿Cuál?',['Vuelos','Restaurantes','Alquiler','Conciertos']),
 ('know','{s} se queda ocho horas tirado/a en un aeropuerto. ¿Plan de supervivencia?',['Busca sala VIP','Sale a conocer la ciudad','Se queja con arte','Duerme donde sea']),
 ('know','A {s} le toca poner música en un viaje en coche. ¿Qué pone?',['Hits para todos','Su playlist rara','Temazos antiguos','Le pasa el móvil a otro']),
 ('know','{s} consigue una hora sin obligaciones ni notificaciones. ¿Qué hace?',['Siesta','Paseo','Ve algo','Llama a alguien']),
 ('know','{s} tiene que organizar una cena casi sin aviso. ¿Qué pasa?',['Cocina de verdad','Pide todo','Monta picoteo y copas','Entra en pánico y al final sale bien']),
 ('know','{s} puede volverse buenísimo/a en algo de golpe. ¿Qué elige?',['Un idioma','Cocinar','Música','Negocios']),
 ('room','¿A quién de aquí confiaría {s} una sorpresa sin que la arruine?',[]),
 ('room','¿Quién de aquí haría reír a {s} justo cuando no debería?',[]),
 ('room','¿A quién llamaría {s} primero para pedir una opinión brutalmente sincera?',[]),
 ('room','¿Con quién de aquí aguantaría {s} feliz un viaje de 12 horas?',[]),
],
'pt-BR':[
 ('know','{s} ganha amanhã inteiro livre, sem obrigação nenhuma. O que faz primeiro?',['Dorme até tarde','Marca algo de última hora','Chama os amigos','Resolve aquilo que vive adiando']),
 ('know','{s} entra num restaurante com um cardápio gigante. Como escolhe?',['Vai no mais diferente','Pede o de sempre','Pergunta ao garçom','Pede várias coisas pra dividir']),
 ('know','{s} acha uma passagem ridiculamente barata saindo hoje à noite. O que faz?',['Compra na hora','Pesquisa tudo antes','Manda no grupo','Desiste porque é caos demais']),
 ('know','Um amigo cancela com {s} pela terceira vez em cima da hora. Reação?',['Fala na lata','Dá mais uma chance','Se afasta','Ri, mas guarda na memória']),
 ('know','{s} ganha R$ 5.000 que só podem ser gastos com diversão. Pra onde vai?',['Fim de semana fora','Compras','Jantar incrível pra galera','Algo que queria há tempos']),
 ('know','{s} está atrasado/a. O que provavelmente está acontecendo?',['Ainda escolhendo roupa','Procurando a chave','Falando “tô chegando” de casa','Realmente já saiu']),
 ('know','Chega pra {s}: “precisamos conversar”. Primeiro pensamento?',['O que eu fiz?','Lá vem drama','Liga na hora','Finge que ainda não viu']),
 ('know','{s} precisa ficar um mês sem um app. Qual vai embora?',['Instagram','TikTok','Apps de namoro','Delivery']),
 ('know','Toca em público uma música que {s} ama. O que acontece?',['Canta sem vergonha','Dança de leve','Só sorri','Grava e manda no grupo']),
 ('know','Domingo perfeito e sem compromisso pra {s}. O que vence?',['Cama e série','Praia ou parque','Almoço longo com amigos','Dia totalmente improvisado']),
 ('know','{s} compra celular novo. O que faz primeiro?',['Passa tudo pro aparelho','Testa a câmera','Organiza os apps','Deixa pra configurar depois']),
 ('know','O plano da galera desanda uma hora antes. Qual é o papel de {s}?',['Salva o rolê','Curte o caos','Fica irritado/a','Transforma em piada']),
 ('know','{s} pode morar seis meses em qualquer lugar com aluguel pago. O que mais importa?',['Praia','Cidade grande','Natureza','Ficar perto de quem ama']),
 ('know','Numa viagem oferecem pra {s} uma atividade que dá medo, mas é segura. Resposta?',['Bora agora','Precisa convencer','Só se todo mundo for','Nem pensar']),
 ('know','{s} posta um story e se arrepende dois minutos depois. O que faz?',['Apaga','Deixa lá','Vê quem já assistiu','Pergunta pra um amigo se ficou vergonha alheia']),
 ('know','Um desconhecido elogia {s} do nada. Reação?',['Aceita e curte','Fica sem graça','Faz piada','Pensa nisso o dia inteiro']),
 ('know','{s} pode ter uma coisa de graça pra sempre. Qual?',['Passagens','Restaurantes','Aluguel','Shows']),
 ('know','{s} fica preso/a oito horas num aeroporto. Plano de sobrevivência?',['Caça uma sala VIP','Sai pra conhecer a cidade','Reclama com categoria','Dorme em qualquer canto']),
 ('know','{s} fica com o som numa viagem de carro. Qual é a vibe?',['Hits que todo mundo conhece','Playlist própria e específica','Só nostalgia','Passa o celular pra outra pessoa']),
 ('know','{s} ganha uma hora sem responsabilidade e sem notificação. O que faz?',['Cochila','Sai pra andar','Assiste alguma coisa','Liga pra alguém']),
 ('know','{s} precisa receber gente pra jantar quase sem aviso. O que rola?',['Cozinha de verdade','Pede tudo','Faz petiscos e bebida','Entra em pânico e no fim dá certo']),
 ('know','{s} pode ficar excelente em uma coisa instantaneamente. O que escolhe?',['Um idioma','Cozinhar','Música','Negócios']),
 ('room','Em quem daqui {s} confiaria pra preparar uma surpresa sem estragar tudo?',[]),
 ('room','Quem daqui faria {s} rir exatamente na hora errada?',[]),
 ('room','Pra quem daqui {s} ligaria primeiro querendo uma opinião 100% sincera?',[]),
 ('room','Com quem daqui {s} toparia ficar preso/a numa viagem de 12 horas?',[]),
],
'fr':[
 ('know','{s} a toute sa journée de demain libre, sans aucune obligation. Première chose?',['Faire la grasse matinée','Réserver un truc spontané','Voir des amis','Faire enfin ce qui traîne depuis des semaines']),
 ('know','{s} arrive dans un resto avec une carte immense. Comment choisir?',['Le plat le plus bizarre','Une valeur sûre','Demander au serveur','Commander plusieurs trucs à partager']),
 ('know','{s} trouve un vol absurdement pas cher qui part ce soir. Réaction?',['Réserver direct','Tout vérifier pendant une heure','L’envoyer au groupe','Laisser tomber, trop chaotique']),
 ('know','Un ami annule avec {s} à la dernière minute pour la troisième fois. Réaction?',['Le dire franchement','Donner encore une chance','Prendre ses distances','En rire mais ne pas oublier']),
 ('know','{s} reçoit 1 000 € à dépenser uniquement pour le plaisir. Ça part où?',['Un week-end','Du shopping','Un super dîner pour tout le monde','Un truc voulu depuis longtemps']),
 ('know','{s} est en retard. Qu’est-ce qui se passe vraiment?',['Toujours en train de choisir sa tenue','Cherche ses clés','Dit “j’arrive” depuis chez soi','Est vraiment déjà en route']),
 ('know','{s} reçoit “il faut qu’on parle”. Première pensée?',['Qu’est-ce que j’ai fait?','Ça sent le drama','Appelle tout de suite','Fait semblant de ne pas avoir vu']),
 ('know','{s} doit supprimer une appli pendant un mois. Laquelle saute?',['Instagram','TikTok','Applis de rencontre','Livraison de repas']),
 ('know','Une chanson que {s} adore passe en public. Que se passe-t-il?',['Chante sans honte','Petit pas de danse','Sourit juste','Filme pour l’envoyer au groupe']),
 ('know','Dimanche parfait sans aucun plan pour {s}. Le programme?',['Lit et séries','Plage ou parc','Long repas avec des amis','Journée totalement improvisée']),
 ('know','{s} change de téléphone. Première chose?',['Tout transférer','Tester l’appareil photo','Ranger les applis','Remettre la configuration à plus tard']),
 ('know','Le plan du groupe tombe à l’eau une heure avant. Quel rôle prend {s}?',['Sauve le plan','Profite du chaos','S’énerve','En fait une blague']),
 ('know','{s} peut vivre six mois n’importe où, loyer payé. Le plus important?',['La mer','Une grande ville','La nature','Être proche de ses proches']),
 ('know','En vacances, on propose à {s} une activité flippante mais sûre. Réponse?',['Oui direct','Il faut convaincre','Seulement si tout le monde vient','Jamais de la vie']),
 ('know','{s} poste une story et regrette deux minutes après. Que fait-il/elle?',['Supprime','La laisse','Regarde qui l’a déjà vue','Demande à un ami si c’était gênant']),
 ('know','Un inconnu fait un compliment inattendu à {s}. Réaction?',['L’assume','Devient timide','Fait une blague','Y pense toute la journée']),
 ('know','{s} peut avoir une chose gratuite à vie. Laquelle?',['Les vols','Les restos','Le loyer','Les concerts']),
 ('know','{s} est bloqué huit heures à l’aéroport. Plan de survie?',['Trouver un lounge','Sortir visiter la ville','Se plaindre avec panache','Dormir n’importe où']),
 ('know','{s} gère la musique pendant un road trip. Quelle ambiance?',['Des tubes pour tout le monde','Sa playlist très perso','Des vieux hits','Laisse quelqu’un d’autre gérer']),
 ('know','{s} gagne une heure sans responsabilité ni notification. Que fait-il/elle?',['Sieste','Balade','Regarder quelque chose','Appeler quelqu’un']),
 ('know','{s} doit recevoir à dîner presque sans prévenir. Que se passe-t-il?',['Cuisine vraiment','Commande tout','Fait apéro et grignotage','Panique puis s’en sort très bien']),
 ('know','{s} peut devenir excellent dans un domaine instantanément. Lequel?',['Une langue','La cuisine','La musique','Le business']),
 ('room','À qui ici {s} ferait confiance pour organiser une surprise sans tout gâcher?',[]),
 ('room','Qui ici ferait rire {s} au pire moment possible?',[]),
 ('room','Qui {s} appellerait en premier pour avoir un avis vraiment honnête?',[]),
 ('room','Avec qui ici {s} supporterait volontiers un trajet de 12 heures?',[]),
],
'ar':[
 ('know','فجأة صار بكرة كله فاضي عند {s} وما عنده أي التزام. أول شيء يسويه؟',['ينام للظهر','يحجز شيء عالسريع','يرتب طلعة مع أصحابه','ينجز الشيء اللي مأجله من زمان']),
 ('know','{s} يدخل مطعم والمنيو طويل بشكل مبالغ فيه. كيف يختار؟',['أغرب طبق','شيء يعرفه ويضمنه','يسأل الجرسون','يطلب أشياء للمشاركة']),
 ('know','{s} يلاقي تذكرة سفر رخيصة بشكل جنوني وموعدها الليلة. ماذا يفعل؟',['يحجز فوراً','يبحث عن كل التفاصيل','يرسلها للجروب','يقرر أن الموضوع فوضى زيادة']),
 ('know','صديق يلغي على {s} آخر لحظة للمرة الثالثة. ردة الفعل؟',['يقول له بصراحة','يعطيه فرصة ثانية','يبعد شوي','يضحك عليها لكنه يتذكر']),
 ('know','{s} يحصل على مبلغ لازم يصرفه كله على المتعة فقط. وين يروح؟',['ويكند سفر','تسوق','عشاء رهيب للجميع','شيء يتمناه من زمان']),
 ('know','{s} متأخر. إيش غالباً قاعد يصير؟',['لسه يختار اللبس','يدور المفاتيح','يقول “دقيقتين” وهو بالبيت','فعلاً بالطريق']),
 ('know','تجي {s} رسالة: “لازم نتكلم”. أول فكرة؟',['أنا إيش سويت؟','واضح في دراما','يتصل فوراً','يسوي نفسه ما شاف']),
 ('know','{s} لازم يحذف تطبيق شهر كامل. أي واحد يروح؟',['إنستغرام','تيك توك','تطبيقات المواعدة','توصيل الأكل']),
 ('know','تشتغل أغنية يحبها {s} قدام الناس. إيش يصير؟',['يغني بدون خجل','يرقص شوي','بس يبتسم','يصورها ويرسلها للجروب']),
 ('know','الأحد المثالي عند {s} بدون أي خطط. مين يفوز؟',['سرير ومسلسلات','بحر أو حديقة','أكلة طويلة مع الأصحاب','يوم كله عفوي']),
 ('know','{s} يشتري جوال جديد. أول شيء؟',['ينقل كل شيء','يجرب الكاميرا','يرتب التطبيقات','يأجل الإعداد لبعدين']),
 ('know','خطة الجروب تخرب قبلها بساعة. دور {s} الطبيعي؟',['ينقذ الخطة','يستمتع بالفوضى','يتنرفز','يحولها لنكتة']),
 ('know','{s} يقدر يعيش ستة أشهر بأي مكان والإيجار مدفوع. الأهم؟',['البحر','مدينة كبيرة','الطبيعة','القرب من الناس اللي يحبهم']),
 ('know','في السفر يعرضون على {s} نشاط يخوف لكنه آمن. الرد؟',['أكيد يلا','يحتاج إقناع','بس لو الكل راح','مستحيل']),
 ('know','{s} ينزل ستوري ويندم بعد دقيقتين. ماذا يفعل؟',['يحذفه','يخليه','يشوف مين شافه','يسأل صاحبه إذا كان محرج']),
 ('know','شخص غريب يمدح {s} فجأة. ردة الفعل؟',['يأخذ المدح بثقة','يستحي','يمزح','يفكر فيه طول اليوم']),
 ('know','{s} يقدر يحصل على شيء واحد مجاناً طول العمر. إيش يختار؟',['تذاكر سفر','مطاعم','إيجار','حفلات']),
 ('know','{s} عالق ثماني ساعات في المطار. خطة النجاة؟',['يدور لاونج','يطلع يشوف المدينة','يشتكي بكل دراما','ينام بأي مكان']),
 ('know','{s} مسؤول عن الموسيقى في رحلة سيارة. إيش يشغل؟',['أغاني يحبها الكل','بلاي ليست خاصة جداً','أغاني قديمة ونوستالجيا','يعطي المهمة لشخص ثاني']),
 ('know','{s} يحصل على ساعة بدون مسؤوليات ولا إشعارات. ماذا يفعل؟',['غفوة','يمشي شوي','يتفرج على شيء','يتصل بأحد']),
 ('know','{s} لازم يعزم ناس على عشاء بدون تحضير تقريباً. إيش يصير؟',['يطبخ بجد','يطلب كل شيء','يسوي سناكات ومشروبات','يتوتر وبالأخير يضبطها']),
 ('know','{s} يقدر يصير ممتاز فوراً في شيء واحد. إيش يختار؟',['لغة','طبخ','موسيقى','بيزنس']),
 ('room','مين هنا يثق فيه {s} يرتب له مفاجأة بدون ما يخربها؟',[]),
 ('room','مين هنا ممكن يضحك {s} في أسوأ وقت ممكن؟',[]),
 ('room','مين أول شخص هنا يتصل فيه {s} لو يبغى رأي صريح جداً؟',[]),
 ('room','مع مين هنا يقدر {s} يتحمل رحلة 12 ساعة وهو مبسوط؟',[]),
],
}

SPICY_BY_LANG = {
'en':[
 ('know','What creates instant chemistry for {s}?',['Eye contact','Sharp humor','Confidence','That impossible-to-explain spark']),
 ('know','On a dating app, what makes {s} reply fastest?',['A great photo','A funny bold opener','Straightforward energy','A profile with real personality']),
 ('know','What kills attraction fastest for {s}?',['Too much ego','Zero humor','Playing games','Bad communication']),
 ('know','On a date with great chemistry, what is most like {s}?',['Takes the lead','Lets the other person lead','Just follows the vibe','Messages a friend “oh no, this is good”']),
 ('know','For {s}, what matters most in good sexual chemistry?',['Strong attraction','Confidence','Open communication','Playfulness']),
 ('know','A casual night with no pressure: what sounds most like {s}?',['A date that gets flirty fast','A spontaneous meetup','Flirting with no plan','Staying with friends after all']),
],
'es':[
 ('know','¿Qué crea química instantánea para {s}?',['Contacto visual','Humor rápido','Seguridad','Esa chispa imposible de explicar']),
 ('know','En una app de citas, ¿qué hace que {s} responda más rápido?',['Una foto brutal','Una apertura atrevida y graciosa','Ir directo al grano','Un perfil con personalidad']),
 ('know','¿Qué mata la atracción más rápido para {s}?',['Demasiado ego','Cero humor','Jueguitos','Mala comunicación']),
 ('know','En una cita con mucha química, ¿qué pega más con {s}?',['Toma la iniciativa','Deja que lidere la otra persona','Se deja llevar','Escribe a un amigo “esto pinta demasiado bien”']),
 ('know','Para {s}, ¿qué pesa más en una buena química sexual?',['Mucha atracción','Seguridad','Comunicación abierta','Juego y picante']),
 ('know','Noche casual y sin presión: ¿qué suena más a {s}?',['Una cita que se calienta rápido','Quedar de forma espontánea','Flirtear sin plan','Acabar con los amigos']),
],
'pt-BR':[
 ('know','O que cria química instantânea pra {s}?',['Contato visual','Humor afiado','Confiança','Aquela faísca difícil de explicar']),
 ('know','Num app de namoro, o que faz {s} responder mais rápido?',['Uma foto ótima','Uma abertura ousada e engraçada','Direto ao ponto','Perfil com personalidade']),
 ('know','O que mata a atração mais rápido pra {s}?',['Ego demais','Zero humor','Joguinhos','Comunicação ruim']),
 ('know','Num date com muita química, o que combina mais com {s}?',['Toma a iniciativa','Deixa a outra pessoa conduzir','Vai no clima','Manda pro amigo “isso tá bom demais”']),
 ('know','Pra {s}, o que pesa mais numa boa química sexual?',['Atração forte','Confiança','Comunicação aberta','Leveza e provocação']),
 ('know','Noite casual e sem pressão: o que mais parece {s}?',['Date que esquenta rápido','Encontro de última hora','Flertar sem plano','Acabar ficando com os amigos']),
],
'fr':[
 ('know','Qu’est-ce qui crée une alchimie immédiate pour {s}?',['Le regard','Un humour piquant','La confiance','Ce truc impossible à expliquer']),
 ('know','Sur une appli de rencontre, qu’est-ce qui fait répondre {s} le plus vite?',['Une super photo','Une accroche drôle et culottée','Quelqu’un de direct','Un profil avec une vraie personnalité']),
 ('know','Qu’est-ce qui casse l’attirance le plus vite pour {s}?',['Trop d’ego','Zéro humour','Les jeux','Une mauvaise communication']),
 ('know','Sur un date avec beaucoup d’alchimie, qu’est-ce qui ressemble le plus à {s}?',['Prend les devants','Laisse l’autre mener','Suit le feeling','Écrit à un ami “ok, ça devient sérieux”']),
 ('know','Pour {s}, le plus important dans une bonne alchimie sexuelle?',['Une forte attirance','La confiance','Une communication ouverte','Le jeu et le fun']),
 ('know','Une soirée casual sans pression: qu’est-ce qui ressemble le plus à {s}?',['Un date qui devient vite flirt','Une rencontre spontanée','Flirter sans plan','Finalement rester avec les amis']),
],
'ar':[
 ('know','إيش أسرع شيء يصنع كيمياء عند {s}?',['نظرات','حس فكاهي قوي','ثقة','شرارة ما لها تفسير']),
 ('know','في تطبيق مواعدة، إيش يخلي {s} يرد أسرع؟',['صورة قوية','افتتاحية جريئة ومضحكة','كلام مباشر','بروفايل فيه شخصية']),
 ('know','إيش يطفّي الانجذاب أسرع عند {s}?',['غرور زيادة','بدون حس فكاهي','ألعاب نفسية','تواصل سيئ']),
 ('know','في موعد فيه كيمياء قوية، إيش الأقرب لـ {s}?',['يبادر','يخلي الطرف الثاني يقود','يمشي مع الجو','يرسل لصاحبه “الموضوع صار خطير”']),
 ('know','إيش الأهم عند {s} في كيمياء جنسية جيدة؟',['انجذاب قوي','ثقة','تواصل مفتوح','خفة ولعب']),
 ('know','ليلة كاجوال وبدون ضغط: إيش يشبه {s} أكثر؟',['موعد يصير فليرتي بسرعة','لقاء عفوي','فليرت بدون خطة','بالأخير يبقى مع الأصحاب']),
],
}

CALLBACK_COPY = {
'en':{
 'friend':('callback','⚡ PLOT TWIST: Earlier, {sub} picked {friend}. Now they have to plan a completely spontaneous day together. What does {sub} think {friend} will suggest first?',['Book something immediately','Start researching everything','Find food or drinks first','Make it up as they go']),
 'old':('callback','⚡ PLOT TWIST: Earlier, {sub} chose “{old}”. Now that choice becomes real tomorrow morning. What does {sub} do first?',['Commits fully','Tries to improve the plan','Panics a little but goes with it','Tries to bring someone along']),
 'duo':('duo_callback','⚡ PLOT TWIST: Earlier, {sub} chose “{old}”. Now it becomes real and there is no cancel button. What happens first?',['Goes all in','Asks for more details','Changes the plan','Makes it even more extreme']),
 'match':'⚡ {a} and {b}: secretly type one place you would escape to tomorrow. Same answer = +1 point each.'
},
'es':{
 'friend':('callback','⚡ PLOT TWIST: Antes, {sub} eligió a {friend}. Ahora tienen que montar juntos un día totalmente improvisado. ¿Qué cree {sub} que propondrá {friend} primero?',['Reservar algo ya','Investigar todo','Buscar comida o copas primero','Improvisar sobre la marcha']),
 'old':('callback','⚡ PLOT TWIST: Antes, {sub} eligió “{old}”. Mañana esa elección se vuelve real. ¿Qué hace {sub} primero?',['Se mete de lleno','Intenta mejorar el plan','Se asusta un poco pero sigue','Intenta llevarse a alguien']),
 'duo':('duo_callback','⚡ PLOT TWIST: Antes, {sub} eligió “{old}”. Ahora se hace realidad y no hay botón de cancelar. ¿Qué pasa primero?',['Va con todo','Pide más detalles','Cambia el plan','Lo lleva todavía más lejos']),
 'match':'⚡ {a} y {b}: escriban en secreto un lugar al que escaparían mañana. Misma respuesta = +1 punto para cada uno.'
},
'pt-BR':{
 'friend':('callback','⚡ PLOT TWIST: Antes, {sub} escolheu {friend}. Agora os dois precisam montar um dia totalmente no improviso. O que {sub} acha que {friend} vai sugerir primeiro?',['Reservar algo na hora','Pesquisar tudo','Comer ou beber primeiro','Ir decidindo pelo caminho']),
 'old':('callback','⚡ PLOT TWIST: Antes, {sub} escolheu “{old}”. Amanhã essa escolha vira realidade. O que {sub} faz primeiro?',['Vai com tudo','Tenta melhorar o plano','Fica meio em pânico, mas vai','Tenta levar alguém junto']),
 'duo':('duo_callback','⚡ PLOT TWIST: Antes, {sub} escolheu “{old}”. Agora virou realidade e não dá pra cancelar. O que acontece primeiro?',['Mergulha de cabeça','Pede mais detalhes','Muda o plano','Deixa tudo ainda mais extremo']),
 'match':'⚡ {a} e {b}: cada um escreve em segredo um lugar pra onde fugiria amanhã. Mesma resposta = +1 ponto pra cada.'
},
'fr':{
 'friend':('callback','⚡ PLOT TWIST: Plus tôt, {sub} a choisi {friend}. Maintenant ils doivent improviser une journée entière ensemble. D’après {sub}, que va proposer {friend} en premier?',['Réserver quelque chose direct','Tout rechercher','Trouver à manger ou à boire','Improviser au fur et à mesure']),
 'old':('callback','⚡ PLOT TWIST: Plus tôt, {sub} a choisi « {old} ». Demain matin, ce choix devient réel. Première réaction?',['Y aller à fond','Améliorer le plan','Paniquer un peu mais suivre','Essayer d’embarquer quelqu’un']),
 'duo':('duo_callback','⚡ PLOT TWIST: Plus tôt, {sub} a choisi « {old} ». Maintenant c’est réel et impossible d’annuler. Que se passe-t-il d’abord?',['Y aller à fond','Demander plus de détails','Changer le plan','Rendre le truc encore plus intense']),
 'match':'⚡ {a} et {b}: écrivez chacun en secret un endroit où vous partiriez demain. Même réponse = +1 point chacun.'
},
'ar':{
 'friend':('callback','⚡ PLOT TWIST: قبل شوي {sub} اختار {friend}. الآن لازم يرتبون يوم كامل عفوي مع بعض. إيش يتوقع {sub} أن {friend} يقترح أول شيء؟',['يحجز شيء فوراً','يبحث عن كل التفاصيل','يدور أكل أو مشروب أول','يمشونها عفوي']),
 'old':('callback','⚡ PLOT TWIST: قبل شوي {sub} اختار “{old}”. بكرة الصباح الاختيار هذا يصير حقيقة. أول شيء يسويه {sub}؟',['يدخل فيها للآخر','يحاول يحسن الخطة','يتوتر شوي لكن يكمل','يحاول يجيب شخص معه']),
 'duo':('duo_callback','⚡ PLOT TWIST: قبل شوي {sub} اختار “{old}”. الآن صار حقيقة وما في زر إلغاء. إيش يصير أول؟',['يدخل بكل قوة','يسأل عن تفاصيل أكثر','يغير الخطة','يصعّدها أكثر']),
 'match':'⚡ {a} و {b}: كل واحد يكتب بالسر مكان واحد يهرب له بكرة. نفس الإجابة = +1 لكل واحد.'
},
}

def general_pack(lang):
    return list(GENERAL_BY_LANG.get(normalize_language(lang), []))

def spicy_pack(lang):
    return list(SPICY_BY_LANG.get(normalize_language(lang), []))

def callback_copy(lang, kind, sub, friend='', old=''):
    lang = normalize_language(lang)
    if lang == 'he':
        return None
    item = CALLBACK_COPY[lang][kind]
    typ, text, opts = item
    return typ, text.format(sub=sub, friend=friend, old=old), list(opts)

def match_prompt(lang, a, b):
    lang = normalize_language(lang)
    if lang == 'he':
        return ''
    return CALLBACK_COPY[lang]['match'].format(a=a, b=b)


UI_COPY = {
'en':{
 'home_title':'Who really knows the crew?','home_sub':'One person answers in secret. Everyone else guesses. The game learns your group as you play.',
 'create':'Create game','join':'Join game','create_title':'What kind of night are you having?','name':'Your name','topics':'What do you want to play about?','topics_hint':'Pick a few topics. Open more if you want.',
 'more':'More topics +','less':'Fewer topics −','rounds':'How many rounds?','spice':'How bold?','prize':'Winner prize (optional)','context':'Tell PlotTwist who you are (optional)','create_room':'Create room',
 'join_title':'Join the crew','room_code':'Room code','join_room':'Join','waiting_host':'Waiting for the host to start','start':'Start game','share':'Share link',
 'answer_saved':'Your answer is saved','guess_saved':'Your guess is saved','waiting_others':'Waiting for the other players','waiting_subject':'Waiting for {name} to answer in secret','reveal':'REVEAL','next':'Next question →',
 'finish':'Who knows the crew best?','play_again':'Play again with the same crew','new_game':'New game','how_title':'How to play','how1':'One player answers in secret.','how2':'Everyone else predicts their answer.','how3':'Correct guess = 1 point.','how4':'Do not reveal the answer before the Reveal.','got_it':'Got it — start',
 'adult':'All players are 18+ and agree to adult content in this room.','language':'Language','selected':'Selected: {topics}','add_topics':'Want to add something?','saved':'Saved','retry':'Try again',
 'family':'Family / Chill','bold':'Bold','no_filter':'No Filter','points':'pts','offline':'offline'
},
'es':{
 'home_title':'¿Quién conoce de verdad al grupo?','home_sub':'Una persona responde en secreto. Los demás adivinan. El juego aprende cómo sois mientras jugáis.',
 'create':'Crear partida','join':'Unirse','create_title':'¿Qué tipo de noche os apetece?','name':'Tu nombre','topics':'¿Sobre qué queréis jugar?','topics_hint':'Elige varios temas. Puedes abrir más cuando quieras.',
 'more':'Más temas +','less':'Menos temas −','rounds':'¿Cuántas rondas?','spice':'¿Qué tan atrevido?','prize':'Premio para quien gane (opcional)','context':'Cuéntale a PlotTwist quiénes sois (opcional)','create_room':'Crear sala',
 'join_title':'Únete al grupo','room_code':'Código de sala','join_room':'Entrar','waiting_host':'Esperando a que el anfitrión empiece','start':'Empezar','share':'Compartir enlace',
 'answer_saved':'Tu respuesta está guardada','guess_saved':'Tu apuesta está guardada','waiting_others':'Esperando al resto','waiting_subject':'Esperando a que {name} responda en secreto','reveal':'REVEAL','next':'Siguiente pregunta →',
 'finish':'¿Quién conoce mejor al grupo?','play_again':'Jugar otra vez con el mismo grupo','new_game':'Nueva partida','how_title':'¿Cómo se juega?','how1':'Una persona responde en secreto.','how2':'Los demás intentan adivinar qué eligió.','how3':'Acierto = 1 punto.','how4':'No reveléis la respuesta antes del Reveal.','got_it':'Entendido — empezar',
 'adult':'Todos los participantes tienen 18+ y aceptan contenido para adultos.','language':'Idioma','selected':'Elegisteis: {topics}','add_topics':'¿Queréis añadir algo?','saved':'Guardado','retry':'Intentar otra vez',
 'family':'Family / Chill','bold':'Bold','no_filter':'No Filter','points':'pts','offline':'sin conexión'
},
'pt-BR':{
 'home_title':'Quem conhece a galera de verdade?','home_sub':'Uma pessoa responde em segredo. Todo mundo tenta adivinhar. O jogo aprende sobre vocês enquanto rola.',
 'create':'Criar jogo','join':'Entrar no jogo','create_title':'Que tipo de noite vocês querem?','name':'Seu nome','topics':'Sobre o que vocês querem jogar?','topics_hint':'Escolha alguns temas. Dá pra abrir mais quando quiser.',
 'more':'Mais temas +','less':'Menos temas −','rounds':'Quantas rodadas?','spice':'Qual o nível de ousadia?','prize':'Prêmio do vencedor (opcional)','context':'Conte ao PlotTwist quem vocês são (opcional)','create_room':'Criar sala',
 'join_title':'Entre na galera','room_code':'Código da sala','join_room':'Entrar','waiting_host':'Esperando o anfitrião começar','start':'Começar jogo','share':'Compartilhar link',
 'answer_saved':'Sua resposta foi salva','guess_saved':'Seu palpite foi salvo','waiting_others':'Esperando o resto da galera','waiting_subject':'Esperando {name} responder em segredo','reveal':'REVEAL','next':'Próxima pergunta →',
 'finish':'Quem conhece melhor a galera?','play_again':'Jogar de novo com a mesma galera','new_game':'Novo jogo','how_title':'Como jogar?','how1':'Uma pessoa responde em segredo.','how2':'Todo mundo tenta prever a resposta.','how3':'Acertou = 1 ponto.','how4':'Não revele a resposta antes do Reveal.','got_it':'Entendi — começar',
 'adult':'Todos os participantes têm 18+ e concordam com conteúdo adulto nesta sala.','language':'Idioma','selected':'Vocês escolheram: {topics}','add_topics':'Querem adicionar algo?','saved':'Salvo','retry':'Tentar de novo',
 'family':'Family / Chill','bold':'Bold','no_filter':'No Filter','points':'pts','offline':'offline'
},
'fr':{
 'home_title':'Qui connaît vraiment le groupe ?','home_sub':'Une personne répond en secret. Les autres devinent. Le jeu apprend à vous connaître au fil des manches.',
 'create':'Créer une partie','join':'Rejoindre','create_title':'Vous voulez quelle ambiance ce soir ?','name':'Ton prénom','topics':'Vous voulez jouer sur quoi ?','topics_hint':'Choisissez quelques thèmes. Vous pourrez en afficher davantage.',
 'more':'Plus de thèmes +','less':'Moins de thèmes −','rounds':'Combien de manches ?','spice':'Quel niveau d’audace ?','prize':'Prix du gagnant (optionnel)','context':'Dites à PlotTwist qui vous êtes (optionnel)','create_room':'Créer la salle',
 'join_title':'Rejoins le groupe','room_code':'Code de la salle','join_room':'Rejoindre','waiting_host':'En attente du lancement par l’hôte','start':'Commencer','share':'Partager le lien',
 'answer_saved':'Ta réponse est enregistrée','guess_saved':'Ton pronostic est enregistré','waiting_others':'On attend les autres joueurs','waiting_subject':'On attend que {name} réponde en secret','reveal':'REVEAL','next':'Question suivante →',
 'finish':'Qui connaît le mieux le groupe ?','play_again':'Rejouer avec le même groupe','new_game':'Nouvelle partie','how_title':'Comment jouer ?','how1':'Une personne répond en secret.','how2':'Les autres essaient de deviner sa réponse.','how3':'Bonne réponse = 1 point.','how4':'Ne révélez rien avant le Reveal.','got_it':'Compris — on joue',
 'adult':'Tous les participants ont 18+ et acceptent le contenu adulte de cette salle.','language':'Langue','selected':'Vous avez choisi : {topics}','add_topics':'Vous voulez ajouter quelque chose ?','saved':'Enregistré','retry':'Réessayer',
 'family':'Family / Chill','bold':'Bold','no_filter':'No Filter','points':'pts','offline':'hors ligne'
},
'ar':{
 'home_title':'مين فعلاً يعرف المجموعة؟','home_sub':'شخص واحد يجاوب بالسر، والباقي يحاولون يخمنون. اللعبة تتعلم عنكم مع كل جولة.',
 'create':'أنشئ لعبة','join':'انضم للعبة','create_title':'أي جو تبغونه الليلة؟','name':'اسمك','topics':'عن إيش تبغون تلعبون؟','topics_hint':'اختاروا كم موضوع، وتقدرون تفتحون مواضيع أكثر.',
 'more':'مواضيع أكثر +','less':'مواضيع أقل −','rounds':'كم جولة؟','spice':'قد إيش تبغونها جريئة؟','prize':'جائزة الفائز (اختياري)','context':'قولوا لـ PlotTwist مين أنتم (اختياري)','create_room':'أنشئ الغرفة',
 'join_title':'ادخل مع المجموعة','room_code':'رمز الغرفة','join_room':'انضم','waiting_host':'ننتظر المضيف يبدأ','start':'ابدأ اللعبة','share':'شارك الرابط',
 'answer_saved':'تم حفظ إجابتك','guess_saved':'تم حفظ تخمينك','waiting_others':'ننتظر باقي اللاعبين','waiting_subject':'ننتظر {name} يجاوب بالسر','reveal':'الكشف','next':'السؤال التالي ←',
 'finish':'مين يعرف المجموعة أكثر؟','play_again':'العبوا مرة ثانية بنفس المجموعة','new_game':'لعبة جديدة','how_title':'كيف نلعب؟','how1':'لاعب واحد يجاوب بالسر.','how2':'الباقي يحاولون يخمنون اختياره.','how3':'تخمين صحيح = نقطة.','how4':'لا تكشفون الإجابة قبل مرحلة الكشف.','got_it':'فهمت — نبدأ',
 'adult':'كل المشاركين أعمارهم 18+ ويوافقون على محتوى للبالغين في هذه الغرفة.','language':'اللغة','selected':'اخترتم: {topics}','add_topics':'تبغون تضيفون شيء؟','saved':'تم الحفظ','retry':'حاول مرة ثانية',
 'family':'Family / Chill','bold':'Bold','no_filter':'No Filter','points':'نقطة','offline':'غير متصل'
},
'he':{
 'home_title':'מי באמת מכיר את החבורה?','home_sub':'אחד עונה בסוד. כולם מנחשים. המשחק לומד אתכם תוך כדי.',
 'create':'צור משחק','join':'הצטרף למשחק','create_title':'איזה ערב בא לכם?','name':'השם שלך','topics':'על מה בא לכם לשחק?','topics_hint':'בחרו כמה נושאים. אפשר לפתוח עוד.',
 'more':'עוד נושאים +','less':'פחות נושאים −','rounds':'כמה סיבובים?','spice':'רמת החריפות','prize':'פרס למנצח (אופציונלי)','context':'ספרו ל־PlotTwist מי אתם (אופציונלי)','create_room':'צור חדר',
 'join_title':'נכנסים לחבורה','room_code':'קוד חדר','join_room':'הצטרף','waiting_host':'מחכים למארח להתחיל','start':'מתחילים','share':'שתף לינק',
 'answer_saved':'התשובה נשמרה','guess_saved':'הניחוש נשמר','waiting_others':'מחכים לשאר השחקנים','waiting_subject':'מחכים ל־{name} לענות בסוד','reveal':'REVEAL','next':'לשאלה הבאה →',
 'finish':'מי מכיר את החבורה הכי טוב?','play_again':'עוד משחק עם אותה חבורה','new_game':'משחק חדש','how_title':'איך משחקים?','how1':'אחד השחקנים עונה בסוד.','how2':'האחרים מנסים לנחש מה הוא בחר.','how3':'ניחוש נכון = נקודה.','how4':'לא מגלים את התשובה לפני ה־Reveal.','got_it':'הבנתי — מתחילים',
 'adult':'כל המשתתפים בני 18 ומעלה ומאשרים תוכן למבוגרים בחדר הזה.','language':'שפה','selected':'בחרתם: {topics}','add_topics':'רוצים להוסיף משהו?','saved':'נשמר','retry':'נסה שוב',
 'family':'Family / Chill','bold':'Bold','no_filter':'No Filter','points':'נק׳','offline':'מנותק/ת'
},
}

def ui_copy(lang):
    return UI_COPY[normalize_language(lang)]


# Japanese launch localization. Arabic data above is intentionally not exposed by
# SUPPORTED_LANGUAGES; Japanese replaces it in the public launch selector.
GENERAL_BY_LANG['ja'] = [
 ('know','{s}は明日、急に予定が全部なくなった。まず何をする？',['二度寝する','勢いでどこか予約する','友達を誘う','ずっと後回しにしてたことをやる']),
 ('know','{s}がメニューの多い店に入った。どうやって決める？',['一番変わった料理','いつもの安心メニュー','店員におすすめを聞く','みんなでシェアできるもの']),
 ('know','{s}が今夜出発の激安航空券を見つけた。どうする？',['即予約','まず徹底的に調べる','グループチャットに送る','急すぎて諦める']),
 ('know','友達が3回連続で直前キャンセル。{s}の反応は？',['はっきり言う','もう一度だけ許す','少し距離を置く','笑うけど覚えておく']),
 ('know','{s}が「楽しいことだけに使える10万円」をもらった。何に使う？',['小旅行','買い物','みんなで豪華な食事','前から欲しかったもの']),
 ('know','{s}が遅刻している。本当は何をしてそう？',['まだ服を選んでる','鍵を探してる','家から「もう着く」と送ってる','本当にもう向かってる']),
 ('know','{s}に「話がある」とメッセージが来た。最初に思うことは？',['何したっけ？','ドラマの予感','すぐ電話する','まだ見てないふり']),
 ('know','{s}が1か月だけアプリを1つ消すなら？',['Instagram','TikTok','マッチングアプリ','フードデリバリー']),
 ('know','{s}の大好きな曲が外で流れた。どうなる？',['普通に歌う','ちょっと踊る','ニヤッとするだけ','撮ってグループに送る']),
 ('know','{s}の理想の日曜日は？',['ベッドと配信','海か公園','友達と長いランチ','完全ノープラン']),
 ('know','{s}が新しいスマホを買った。最初にすることは？',['全部データ移行','カメラを試す','アプリを整理','設定は後回し']),
 ('know','グループの予定が1時間前に崩れた。{s}はどうする？',['代案をまとめる','カオスを楽しむ','イラッとする','笑い話にする']),
 ('know','{s}が家賃無料で半年どこでも住める。何を優先する？',['海','大都市','自然','大切な人の近く']),
 ('know','旅行先で怖いけど安全なアクティビティに誘われた{s}。答えは？',['即やる','説得されたら','みんながやるなら','絶対無理']),
 ('know','{s}がストーリーを投稿して2分後に後悔。どうする？',['すぐ消す','そのまま','誰が見たか確認','友達に「痛い？」と聞く']),
 ('know','知らない人に急に褒められた{s}。反応は？',['素直に喜ぶ','照れる','冗談で返す','一日中思い出す']),
 ('know','{s}が一生無料にできるものを1つ選ぶなら？',['航空券','外食','家賃','ライブ']),
 ('know','{s}が空港で8時間足止め。どう過ごす？',['ラウンジ探し','街に出る','文句を言いまくる','どこでも寝る']),
 ('know','ドライブで{s}が音楽担当。どんな選曲？',['みんなが知ってる曲','自分のこだわりプレイリスト','懐メロ','誰かに任せる']),
 ('know','{s}に通知ゼロ・責任ゼロの1時間ができた。何する？',['昼寝','散歩','何か観る','誰かに電話']),
 ('know','{s}が急に人を家に呼んで夕食を用意することに。どうする？',['ちゃんと作る','全部デリバリー','おつまみとお酒で乗り切る','焦るけど結局なんとかする']),
 ('know','{s}が一瞬で何かの達人になれる。何を選ぶ？',['語学','料理','音楽','ビジネス']),
 ('room','{s}がサプライズ計画を任せるなら、この中の誰？',[]),
 ('room','絶対笑っちゃいけない場面で{s}を笑わせそうなのは誰？',[]),
 ('room','{s}が本音100%の意見を聞きたい時、最初に電話するのは誰？',[]),
 ('room','{s}が12時間の長旅で一緒でも楽しめそうなのは誰？',[]),
]

SPICY_BY_LANG['ja'] = [
 ('know','{s}が初対面で「ちょっと気になる」と思う決め手は？',['目線','ユーモア','自信','説明できない相性']),
 ('know','マッチングアプリで{s}がすぐ返信したくなるのは？',['写真が刺さる','面白い一言','ストレートな誘い','ちょっと危険そうな雰囲気']),
 ('know','{s}が「1杯だけ」と言って出かけた夜。結局どうなりそう？',['二軒目どころじゃない','誰かと仲良くなって消える','みんなを別の店へ連れていく','予定外の相手に連絡する']),
 ('know','強い惹かれ合いがあっても、{s}が一気に冷めるのは？',['自信過剰','会話が噛み合わない','駆け引きしすぎ','ユーモアゼロ']),
 ('know','大人の相性で{s}が一番大事にしそうなのは？',['強い魅力','安心感','オープンな会話','遊び心']),
 ('know','{s}がデートで「この人アリかも」と思う瞬間は？',['会話が止まらない','自然に笑える','距離感がちょうどいい','次の予定を聞かれる'])
]

CALLBACK_COPY['ja'] = {
 'friend':('callback','⚡ PLOT TWIST：さっき{sub}は{friend}を選んだ。今度は2人で完全ノープランの1日を過ごすことに。{sub}は{friend}が最初に何を提案すると思う？',['とりあえず何か予約','全部調べ始める','まず食べるか飲む','その場で決める']),
 'old':('callback','⚡ PLOT TWIST：さっき{sub}は「{old}」を選んだ。明日の朝、それが本当に現実になる。{sub}が最初にすることは？',['全力で乗る','もっと良いプランにする','少し焦るけど行く','誰かを巻き込む']),
 'duo':('duo_callback','⚡ PLOT TWIST：さっき{sub}は「{old}」を選んだ。今、それが現実になってキャンセル不可。最初にどうする？',['迷わず行く','詳しく聞く','プランを変える','さらに攻める']),
 'match':'⚡ {a} と {b}：明日逃げるならどこ？ 1か所だけ秘密で入力。同じ答えなら2人とも+1点。'
}

UI_COPY['ja'] = {
 'home_title':'本当にみんなのことを知ってるのは誰？','home_sub':'1人が秘密で答える。みんながその答えを予想する。遊ぶほど、グループのことが見えてくる。',
 'create':'ゲームを作る','join':'ゲームに参加','create_title':'今日はどんな夜にする？','name':'あなたの名前','topics':'何について遊ぶ？','topics_hint':'いくつかテーマを選んでください。必要ならもっと表示できます。',
 'more':'テーマをもっと見る +','less':'テーマを減らす −','rounds':'何ラウンド？','spice':'どこまで攻める？','prize':'勝者への賞品（任意）','context':'あなたたちのことをPlotTwistに教えて（任意）','create_room':'ルームを作る',
 'join_title':'グループに参加','room_code':'ルームコード','join_room':'参加する','waiting_host':'ホストが始めるのを待っています','start':'ゲーム開始','share':'リンクを共有',
 'answer_saved':'答えを保存しました','guess_saved':'予想を保存しました','waiting_others':'ほかのプレイヤーを待っています','waiting_subject':'{name}が秘密で答えるのを待っています','reveal':'REVEAL','next':'次の質問 →',
 'finish':'一番みんなを知っていたのは誰？','play_again':'同じメンバーでもう一度','new_game':'新しいゲーム','how_title':'遊び方','how1':'1人が秘密で答えます。','how2':'ほかの人はその答えを予想します。','how3':'正解 = 1ポイント。','how4':'Revealまでは答えを言わないでください。','got_it':'OK — スタート',
 'adult':'全員18歳以上で、このルームの大人向け内容に同意しています。','language':'言語','selected':'選択中：{topics}','add_topics':'何か追加する？','saved':'保存しました','retry':'もう一度',
 'family':'Family / Chill','bold':'Bold','no_filter':'No Filter','points':'点','offline':'オフライン'
}


GAME_UI_EXTRA = {
'en':{
 'round':'Round {n} of {total}','subject_now':'This one is about you. Pick your real answer — everyone else will only see it at Reveal.','subject_done':'✓ Your answer is saved in secret. Now everyone else is guessing.',
 'guess_now':'What do you think {name} will choose? Correct guess = 1 point.','guess_done':'🔒 Your guess: {guess}. It will be revealed when everyone is done.',
 'score_duo':'🎯 Duo: one answers in secret, the other guesses. Correct guess = 1 point. You switch roles every round.','score_group':'🎯 Scoring: correct guess = 1 point. The spotlight player does not score on their own round.',
 'waiting_guesses':'Waiting for guesses{names}…','waiting_rest':'Waiting for the other players{names}…','waiting_answer':'Waiting for {name} to answer in secret…',
 'correct':'🎯 Nailed it! You guessed {guess} — +1 point','wrong':'Not this time — you guessed {guess}. The answer was {answer}','subject_reveal':'💥 Your answer was {answer}. Anyone who guessed it gets a point.',
 'finish_next':'Finish & winner 🏆','continue_without':'Continue without {name}','share_text':'Let’s see who really knows the crew','link_copied':'Link copied','points_short':'pts',
 'prize_banner':'🏆 Tonight’s prize: {prize}','no_context':'No group description added — the game will use your selected topics.','just_glory':'Bragging rights 😎',
 'ai_ready':'✨ AI Images are connected. When a player has a photo, the game can create a custom Reveal.','ai_missing':'⚠️ AI Images are not connected yet. The game still works normally.',
 'short':'Short','regular':'Regular','long':'Long','chill_desc':'Light & fun','bold_desc':'More personal & cheeky','nofilter_desc':'Adults, dating & intimacy',
 'prize_ph':'e.g. winner picks the next bar','context_ph':'Who are you? What do you talk about? What kind of night do you want?'
},
'es':{
 'round':'Ronda {n} de {total}','subject_now':'Esta pregunta es sobre ti. Elige tu respuesta real; los demás no la verán hasta el Reveal.','subject_done':'✓ Tu respuesta está guardada en secreto. Ahora los demás están intentando adivinar.',
 'guess_now':'¿Qué crees que elegirá {name}? Acierto = 1 punto.','guess_done':'🔒 Tu apuesta: {guess}. Se revelará cuando todos terminen.',
 'score_duo':'🎯 Dúo: uno responde en secreto y el otro adivina. Acierto = 1 punto. Cambiáis de rol cada ronda.','score_group':'🎯 Puntuación: acierto = 1 punto. Quien responde no suma en su propia ronda.',
 'waiting_guesses':'Esperando las apuestas{names}…','waiting_rest':'Esperando al resto{names}…','waiting_answer':'Esperando a que {name} responda en secreto…',
 'correct':'🎯 ¡Acertaste! Elegiste {guess} — +1 punto','wrong':'Esta vez no — elegiste {guess}. La respuesta era {answer}','subject_reveal':'💥 Tu respuesta era {answer}. Quien la haya adivinado gana un punto.',
 'finish_next':'Final y ganador 🏆','continue_without':'Continuar sin {name}','share_text':'A ver quién conoce de verdad al grupo','link_copied':'Enlace copiado','points_short':'pts',
 'prize_banner':'🏆 Premio de esta noche: {prize}','no_context':'No añadisteis descripción del grupo; el juego usará los temas elegidos.','just_glory':'Solo el honor 😎',
 'ai_ready':'✨ AI Images está conectado. Con una foto, el juego puede crear un Reveal personalizado.','ai_missing':'⚠️ AI Images todavía no está conectado. El juego funciona igualmente.',
 'short':'Corto','regular':'Normal','long':'Largo','chill_desc':'Ligero y divertido','bold_desc':'Más personal y atrevido','nofilter_desc':'Adultos, citas e intimidad',
 'prize_ph':'p. ej. quien gane elige el próximo bar','context_ph':'¿Quiénes sois? ¿De qué habláis? ¿Qué tipo de noche queréis?'
},
'pt-BR':{
 'round':'Rodada {n} de {total}','subject_now':'Essa pergunta é sobre você. Escolha sua resposta real — a galera só vai ver no Reveal.','subject_done':'✓ Sua resposta foi salva em segredo. Agora a galera está tentando adivinhar.',
 'guess_now':'O que você acha que {name} vai escolher? Acerto = 1 ponto.','guess_done':'🔒 Seu palpite: {guess}. Ele aparece quando todo mundo terminar.',
 'score_duo':'🎯 Duo: um responde em segredo e o outro adivinha. Acertou = 1 ponto. Vocês alternam a cada rodada.','score_group':'🎯 Pontuação: palpite certo = 1 ponto. Quem responde não pontua na própria rodada.',
 'waiting_guesses':'Esperando os palpites{names}…','waiting_rest':'Esperando o resto da galera{names}…','waiting_answer':'Esperando {name} responder em segredo…',
 'correct':'🎯 Acertou! Seu palpite foi {guess} — +1 ponto','wrong':'Dessa vez não — você marcou {guess}. A resposta era {answer}','subject_reveal':'💥 Sua resposta foi {answer}. Quem acertou ganha um ponto.',
 'finish_next':'Final e vencedor 🏆','continue_without':'Continuar sem {name}','share_text':'Vamos ver quem conhece a galera de verdade','link_copied':'Link copiado','points_short':'pts',
 'prize_banner':'🏆 Prêmio de hoje: {prize}','no_context':'Sem descrição da galera — o jogo vai usar os temas escolhidos.','just_glory':'Só a moral 😎',
 'ai_ready':'✨ AI Images está conectado. Com foto, o jogo pode criar um Reveal personalizado.','ai_missing':'⚠️ AI Images ainda não está conectado. O jogo continua funcionando normalmente.',
 'short':'Curto','regular':'Normal','long':'Longo','chill_desc':'Leve e divertido','bold_desc':'Mais pessoal e ousado','nofilter_desc':'Adultos, encontros e intimidade',
 'prize_ph':'ex.: quem ganhar escolhe o próximo bar','context_ph':'Quem são vocês? Sobre o que falam? Que tipo de noite querem?'
},
'fr':{
 'round':'Manche {n} sur {total}','subject_now':'Cette question est pour toi. Choisis ta vraie réponse — les autres ne la verront qu’au Reveal.','subject_done':'✓ Ta réponse est enregistrée en secret. Les autres essaient maintenant de deviner.',
 'guess_now':'D’après toi, que va choisir {name} ? Bonne réponse = 1 point.','guess_done':'🔒 Ton pronostic : {guess}. Il sera révélé quand tout le monde aura fini.',
 'score_duo':'🎯 Duo : l’un répond en secret, l’autre devine. Bonne réponse = 1 point. Vous alternez à chaque manche.','score_group':'🎯 Score : bonne réponse = 1 point. La personne mise en avant ne marque pas sur sa propre manche.',
 'waiting_guesses':'On attend les pronostics{names}…','waiting_rest':'On attend les autres{names}…','waiting_answer':'On attend que {name} réponde en secret…',
 'correct':'🎯 Bien vu ! Tu avais choisi {guess} — +1 point','wrong':'Pas cette fois — tu avais choisi {guess}. La réponse était {answer}','subject_reveal':'💥 Ta réponse était {answer}. Ceux qui l’ont trouvée gagnent un point.',
 'finish_next':'Finale et gagnant 🏆','continue_without':'Continuer sans {name}','share_text':'Voyons qui connaît vraiment le groupe','link_copied':'Lien copié','points_short':'pts',
 'prize_banner':'🏆 Prix de ce soir : {prize}','no_context':'Aucune description du groupe — le jeu utilisera les thèmes choisis.','just_glory':'La gloire seulement 😎',
 'ai_ready':'✨ AI Images est connecté. Avec une photo, le jeu peut créer un Reveal personnalisé.','ai_missing':'⚠️ AI Images n’est pas encore connecté. Le jeu fonctionne quand même normalement.',
 'short':'Court','regular':'Normal','long':'Long','chill_desc':'Léger et fun','bold_desc':'Plus personnel et culotté','nofilter_desc':'Adultes, dating et intimité',
 'prize_ph':'ex. le gagnant choisit le prochain bar','context_ph':'Qui êtes-vous ? De quoi parlez-vous ? Quelle ambiance voulez-vous ?'
},
'ja':{
 'round':'{n} / {total} ラウンド','subject_now':'今回はあなたの質問。自分の本当の答えを選んでください。Revealまでは他の人には見えません。','subject_done':'✓ 答えを秘密で保存しました。今、みんなが予想しています。',
 'guess_now':'{name}はどれを選ぶと思う？ 正解 = 1ポイント。','guess_done':'🔒 あなたの予想：{guess}。全員が終わったらRevealで公開されます。',
 'score_duo':'🎯 Duo：1人が秘密で答え、もう1人が予想。正解 = 1ポイント。毎ラウンド交代します。','score_group':'🎯 スコア：正解予想 = 1ポイント。回答者は自分のラウンドでは得点しません。',
 'waiting_guesses':'予想を待っています{names}…','waiting_rest':'ほかのプレイヤーを待っています{names}…','waiting_answer':'{name}が秘密で答えるのを待っています…',
 'correct':'🎯 正解！ {guess} を選んで +1ポイント','wrong':'今回はハズレ。予想は {guess}、正解は {answer}','subject_reveal':'💥 あなたの答えは {answer}。当てた人に1ポイント。',
 'finish_next':'結果・優勝者へ 🏆','continue_without':'{name}なしで続ける','share_text':'誰が一番みんなを知ってるか勝負しよう','link_copied':'リンクをコピーしました','points_short':'点',
 'prize_banner':'🏆 今日の賞品：{prize}','no_context':'グループ紹介は未入力です。選んだテーマを使ってゲームを作ります。','just_glory':'名誉だけ 😎',
 'ai_ready':'✨ AI Images 接続済み。写真があればカスタムRevealを作れます。','ai_missing':'⚠️ AI Images はまだ未接続です。ゲーム自体は通常どおり遊べます。',
 'short':'短め','regular':'ふつう','long':'長め','chill_desc':'軽く楽しく','bold_desc':'もう少し個人的で大胆','nofilter_desc':'18+・デート・親密な話',
 'prize_ph':'例：勝った人が次のお店を決める','context_ph':'どんなメンバー？ 普段何を話す？ 今日はどんな夜にしたい？'
},
'he':{
 'round':'סיבוב {n} מתוך {total}','subject_now':'זו השאלה שלך. בחר/י את התשובה האמיתית — האחרים לא יראו אותה עד ה־Reveal.','subject_done':'✓ התשובה שלך נשמרה בסוד. עכשיו האחרים מנחשים מה בחרת.',
 'guess_now':'מה לדעתך {name} יבחר/תבחר? ניחוש נכון שווה נקודה.','guess_done':'🔒 הניחוש שלך: {guess}. הוא ייחשף כשכולם יסיימו.',
 'score_duo':'🎯 Duo: אחד עונה בסוד, השני מנחש. ניחוש נכון = נקודה. מתחלפים בכל סיבוב.','score_group':'🎯 ניקוד: ניחוש נכון = נקודה אחת. מי שעונה על עצמו לא מקבל נקודה בסיבוב שלו.',
 'waiting_guesses':'מחכים לניחושים{names}…','waiting_rest':'מחכים לשאר השחקנים{names}…','waiting_answer':'מחכים ל־{name} לענות בסוד…',
 'correct':'🎯 קלעת! ניחשת {guess} — +1 נקודה','wrong':'לא הפעם — ניחשת {guess}. התשובה הייתה {answer}','subject_reveal':'💥 זו הייתה התשובה שלך: {answer}. האחרים מקבלים נקודה אם קלעו.',
 'finish_next':'לסיום ולמנצח 🏆','continue_without':'המשך בלי {name}','share_text':'בואו נראה מי באמת מכיר את החבורה','link_copied':'הלינק הועתק','points_short':'נק׳',
 'prize_banner':'🏆 הפרס הערב: {prize}','no_context':'לא נוסף תיאור — המשחק ישתמש בנושאים שבחרתם.','just_glory':'רק הכבוד 😎',
 'ai_ready':'✨ AI Images מחוברות — כשיש תמונה, המשחק יכול ליצור Reveal מותאם.','ai_missing':'⚠️ AI Images עדיין לא מחוברות. המשחק ממשיך לעבוד כרגיל.',
 'short':'קצר','regular':'רגיל','long':'ארוך','chill_desc':'קליל וכיפי','bold_desc':'יותר אישי וחצוף','nofilter_desc':'למבוגרים, דייטים ומיניות',
 'prize_ph':'למשל: המנצח בוחר את הבר הבא','context_ph':'מי אתם? על מה אתם מדברים? איזה ערב אתם רוצים?'
}
}
for _lang,_extra in GAME_UI_EXTRA.items():
    if _lang in UI_COPY: UI_COPY[_lang].update(_extra)


# Final launch UI polish: every user-visible transient state has native copy.
POLISH_UI_EXTRA = {
'en':{
 'all_topics_selected':'You already selected every available topic 😄','max_topics':'You can add up to 6 topics','adult_topic_requires':'The host must confirm an 18+ room before adding intimacy','save_failed':'Couldn’t save that','game_updated':'✓ Game updated for everyone',
 'choose_image':'Choose an image','image_too_large':'Choose an image under 12 MB','preparing_image':'Preparing your photo…','image_ready':'Photo ready to save.','image_read_failed':'Couldn’t read that image','choose_image_first':'Choose a photo first','photo_consent_required':'Please approve photo use first','room_connection_lost':'Room connection was lost — rejoin from the link','saving':'Saving…','uploading_photo':'Uploading photo…','photo_saved':'✓ Photo saved','not_saved':'Not saved','save_photo':'Save photo',
 'name_required':'Enter your name','joining':'Joining…','retry_join':'Trying again…','game_started':'The game already started','removed':'The host already continued without you','slow_server':'The server is taking a while — try again','join_failed':'Couldn’t join','old_room_missing':'That old room no longer exists — you can start a new game',
 'score_tied':'🔥 It’s tight! Anyone can still win.','leader_one':'⚡ {name} leads by just one point!','leader_now':'🏆 {name} is leading right now','photo_count':'📸 {done} of {total} players added a photo. For the best visual reveals, everyone should add one.','photo_ready':'✓ Your photo is ready for Reveal','winner_prize':'🏆 {name} wins the prize: {prize}',
 'final_ai_missing':'⚠️ The AI poster wasn’t available this time. The game still finished normally.','ai_reveal_ready':'✨ AI REVEAL — a new image was created for this round','ai_reveal_generating':'✨ Creating your AI Reveal… the game can keep moving.','ai_image_missing':'⚠️ The AI image wasn’t created this time — keep playing.',
 'interactive_live':'⚡ Now it leaves the screen','match_yes':'🎯 MATCH! +1 point each','match_no':'😄 No match this time — keep going','secret_short':'Short answer — secret','save_secret':'Save secret answer','match_saved':'🔒 Your secret answer is saved','match_waiting':'👀 Waiting for both players','match_wait_text':'We’ll reveal the Match when both answers are in.','short_answer_required':'Type a short answer','answer_saving':'✓ Saving…','match_save_failed':'Couldn’t save the Match answer',
 'no_previous':'There isn’t a previous round yet','back_game':'✕ Back to game','previous_view':'Previous round — view only','answered':'{name} answered:','previous_note':'You can look back here without changing the game or score.',
 'custom_short_required':'Type a short answer','answer_received':'✓ Answer received','saving_secret':'Saving it secretly and updating the game…','choice_received':'✓ Choice received','saving_update':'Saving and updating the game…','connection_slow':'Connection is slow — try again','retry':'Try again',
 'back_lobby_ok':'Back in the lobby — invite whoever was missing','reopen_too_late':'It’s too late to return to the lobby','replay_loading':'Preparing a new game…','replay_new_questions':'Same crew, fresh questions 🔥','replay_failed':'Couldn’t start the replay',
 'duo_finishes':' — the game will finish with the remaining player','advanced_next':' — moved to the next question','need_two':'At least two players are needed to continue','remove_failed':'Couldn’t remove that player',
 'starting':'⚡ Starting…','game_ready':'✓ Game ready','start_failed':'Couldn’t start — at least 2 players are needed','skipped_no_score':'Skipped with no score','skip_failed':'Couldn’t skip','wait_match_answers':'Waiting for both Match answers','wait_all_guesses':'Waiting for all guesses',
 'photo_button':'📸 Add / replace photo','photo_title':'📸 Your photo','photo_help':'Optional. We only use it to create a fun cinematic Reveal in this private game.','photo_consent':'I agree to use this photo in this private game.','custom_prompt':'✏️ What’s your answer?','custom_placeholder':'Write a short, funny, honest answer…','guess_board':'👀 What did everyone guess?','score_continue':'Continuing in a moment…',
 'lobby_game':'🎭 Your game — everyone can see','topics_label':'Topics:','length_label':'Length:','level_label':'Level:','about_label':'About us:','prize_label':'🏆 Prize:','lobby_note':'The host sets the base. Each player can add up to 6 extra topics.','add_topics_note':'Each player can add up to 6 topics beyond the host’s choices.','edit_game':'✏️ Edit game','edit_title':'✏️ Edit game before starting','save_changes':'Save changes','cancel':'Cancel','rounds_word':'rounds',
 'final_hero_generating':'🎬 Creating the crew’s final poster…','hero_generating_static':'✨ Creating a cinematic Reveal… the game continues normally.'
},
'es':{
 'all_topics_selected':'Ya elegisteis todos los temas disponibles 😄','max_topics':'Puedes añadir hasta 6 temas','adult_topic_requires':'El anfitrión debe confirmar una sala 18+ para añadir intimidad','save_failed':'No se pudo guardar','game_updated':'✓ Partida actualizada para todos',
 'choose_image':'Elige una imagen','image_too_large':'Elige una imagen de menos de 12 MB','preparing_image':'Preparando la foto…','image_ready':'Foto lista para guardar.','image_read_failed':'No pudimos leer esa imagen','choose_image_first':'Elige una foto primero','photo_consent_required':'Primero acepta el uso de la foto','room_connection_lost':'Se perdió la conexión con la sala — vuelve a entrar desde el enlace','saving':'Guardando…','uploading_photo':'Subiendo foto…','photo_saved':'✓ Foto guardada','not_saved':'No se guardó','save_photo':'Guardar foto',
 'name_required':'Escribe tu nombre','joining':'Entrando…','retry_join':'Probando otra vez…','game_started':'La partida ya empezó','removed':'El anfitrión ya siguió sin ti','slow_server':'El servidor está tardando — prueba otra vez','join_failed':'No se pudo entrar','old_room_missing':'Esa sala ya no existe — puedes crear una nueva partida',
 'score_tied':'🔥 ¡Está apretadísimo! Todavía puede ganar cualquiera.','leader_one':'⚡ ¡{name} va primero por solo un punto!','leader_now':'🏆 {name} va en cabeza','photo_count':'📸 {done} de {total} jugadores añadieron foto. Para mejores Reveals, mejor si la suben todos.','photo_ready':'✓ Tu foto está lista para el Reveal','winner_prize':'🏆 {name} gana el premio: {prize}',
 'final_ai_missing':'⚠️ El póster AI no estuvo disponible esta vez. La partida terminó normalmente.','ai_reveal_ready':'✨ AI REVEAL — imagen nueva creada para esta ronda','ai_reveal_generating':'✨ Creando vuestro AI Reveal… podéis seguir jugando.','ai_image_missing':'⚠️ Esta vez no se creó la imagen AI — seguimos jugando.',
 'interactive_live':'⚡ Ahora sale de la pantalla','match_yes':'🎯 ¡MATCH! +1 punto cada uno','match_no':'😄 Esta vez no coincidisteis — seguimos','secret_short':'Respuesta corta — en secreto','save_secret':'Guardar respuesta secreta','match_saved':'🔒 Tu respuesta secreta está guardada','match_waiting':'👀 Esperando a los dos jugadores','match_wait_text':'Cuando respondan los dos veremos si hay Match.','short_answer_required':'Escribe una respuesta corta','answer_saving':'✓ Guardando…','match_save_failed':'No se pudo guardar la respuesta del Match',
 'no_previous':'Todavía no hay una ronda anterior','back_game':'✕ Volver a la partida','previous_view':'Ronda anterior — solo lectura','answered':'{name} respondió:','previous_note':'Puedes mirar atrás sin cambiar la partida ni la puntuación.',
 'custom_short_required':'Escribe una respuesta corta','answer_received':'✓ Respuesta recibida','saving_secret':'Guardándola en secreto y actualizando la partida…','choice_received':'✓ Elección recibida','saving_update':'Guardando y actualizando…','connection_slow':'La conexión va lenta — prueba otra vez','retry':'Intentar otra vez',
 'back_lobby_ok':'De vuelta al lobby — podéis invitar a quien faltaba','reopen_too_late':'Ya es demasiado tarde para volver al lobby','replay_loading':'Preparando otra partida…','replay_new_questions':'Mismo grupo, preguntas nuevas 🔥','replay_failed':'No se pudo iniciar la revancha',
 'duo_finishes':' — la partida terminará con el jugador que queda','advanced_next':' — pasamos a la siguiente pregunta','need_two':'Hacen falta al menos dos jugadores','remove_failed':'No se pudo quitar al jugador',
 'starting':'⚡ Empezando…','game_ready':'✓ Partida lista','start_failed':'No se pudo empezar — hacen falta al menos 2 jugadores','skipped_no_score':'Saltada sin puntuación','skip_failed':'No se pudo saltar','wait_match_answers':'Esperando las dos respuestas del Match','wait_all_guesses':'Esperando todas las apuestas',
 'photo_button':'📸 Añadir / cambiar foto','photo_title':'📸 Tu foto','photo_help':'Opcional. Solo la usamos para crear un Reveal cinematográfico y divertido en esta partida privada.','photo_consent':'Acepto usar esta foto en esta partida privada.','custom_prompt':'✏️ ¿Cuál es tu respuesta?','custom_placeholder':'Escribe una respuesta corta, divertida y real…','guess_board':'👀 ¿Qué apostó cada uno?','score_continue':'Seguimos en un momento…',
 'lobby_game':'🎭 Vuestra partida — todos la ven','topics_label':'Temas:','length_label':'Duración:','level_label':'Nivel:','about_label':'Quiénes somos:','prize_label':'🏆 Premio:','lobby_note':'El anfitrión marca la base. Cada jugador puede añadir hasta 6 temas extra.','add_topics_note':'Cada jugador puede añadir hasta 6 temas además de los elegidos por el anfitrión.','edit_game':'✏️ Editar partida','edit_title':'✏️ Editar antes de empezar','save_changes':'Guardar cambios','cancel':'Cancelar','rounds_word':'rondas',
 'final_hero_generating':'🎬 Creando el póster final del grupo…','hero_generating_static':'✨ Creando un Reveal cinematográfico… la partida sigue normalmente.'
},
'pt-BR':{
 'all_topics_selected':'Vocês já escolheram todos os temas disponíveis 😄','max_topics':'Dá para adicionar até 6 temas','adult_topic_requires':'O anfitrião precisa confirmar sala 18+ antes de adicionar intimidade','save_failed':'Não deu para salvar','game_updated':'✓ Jogo atualizado para todo mundo',
 'choose_image':'Escolha uma imagem','image_too_large':'Escolha uma imagem com menos de 12 MB','preparing_image':'Preparando a foto…','image_ready':'Foto pronta para salvar.','image_read_failed':'Não deu para ler essa imagem','choose_image_first':'Escolha uma foto primeiro','photo_consent_required':'Primeiro aceite o uso da foto','room_connection_lost':'A conexão com a sala caiu — entre de novo pelo link','saving':'Salvando…','uploading_photo':'Enviando foto…','photo_saved':'✓ Foto salva','not_saved':'Não foi salva','save_photo':'Salvar foto',
 'name_required':'Digite seu nome','joining':'Entrando…','retry_join':'Tentando de novo…','game_started':'O jogo já começou','removed':'O anfitrião já continuou sem você','slow_server':'O servidor está demorando — tente de novo','join_failed':'Não deu para entrar','old_room_missing':'Essa sala não existe mais — você pode criar um jogo novo',
 'score_tied':'🔥 Tá apertado! Ainda dá para qualquer um ganhar.','leader_one':'⚡ {name} está na frente por só um ponto!','leader_now':'🏆 {name} está liderando','photo_count':'📸 {done} de {total} jogadores colocaram foto. Para Reveals melhores, vale todo mundo colocar.','photo_ready':'✓ Sua foto está pronta para o Reveal','winner_prize':'🏆 {name} ganhou o prêmio: {prize}',
 'final_ai_missing':'⚠️ O pôster AI não ficou disponível desta vez. O jogo terminou normalmente.','ai_reveal_ready':'✨ AI REVEAL — imagem nova criada para esta rodada','ai_reveal_generating':'✨ Criando o AI Reveal… o jogo pode continuar.','ai_image_missing':'⚠️ A imagem AI não foi criada desta vez — seguimos o jogo.',
 'interactive_live':'⚡ Agora sai da tela','match_yes':'🎯 MATCH! +1 ponto para cada','match_no':'😄 Dessa vez não bateu — bora seguir','secret_short':'Resposta curta — em segredo','save_secret':'Salvar resposta secreta','match_saved':'🔒 Sua resposta secreta foi salva','match_waiting':'👀 Esperando os dois jogadores','match_wait_text':'Quando os dois responderem, a gente revela o Match.','short_answer_required':'Escreva uma resposta curta','answer_saving':'✓ Salvando…','match_save_failed':'Não deu para salvar a resposta do Match',
 'no_previous':'Ainda não tem rodada anterior','back_game':'✕ Voltar ao jogo','previous_view':'Rodada anterior — só para ver','answered':'{name} respondeu:','previous_note':'Dá para olhar aqui sem mudar o jogo nem a pontuação.',
 'custom_short_required':'Escreva uma resposta curta','answer_received':'✓ Resposta recebida','saving_secret':'Salvando em segredo e atualizando o jogo…','choice_received':'✓ Escolha recebida','saving_update':'Salvando e atualizando…','connection_slow':'A conexão está lenta — tente de novo','retry':'Tentar de novo',
 'back_lobby_ok':'Voltamos ao lobby — dá para chamar quem faltou','reopen_too_late':'Já passou da hora de voltar ao lobby','replay_loading':'Preparando jogo novo…','replay_new_questions':'Mesma galera, perguntas novas 🔥','replay_failed':'Não deu para começar de novo',
 'duo_finishes':' — o jogo termina com quem ficou','advanced_next':' — fomos para a próxima pergunta','need_two':'É preciso ter pelo menos dois jogadores','remove_failed':'Não deu para remover o jogador',
 'starting':'⚡ Começando…','game_ready':'✓ Jogo pronto','start_failed':'Não deu para começar — precisa de pelo menos 2 jogadores','skipped_no_score':'Pulamos sem pontuação','skip_failed':'Não deu para pular','wait_match_answers':'Esperando as duas respostas do Match','wait_all_guesses':'Esperando todos os palpites',
 'photo_button':'📸 Adicionar / trocar foto','photo_title':'📸 Sua foto','photo_help':'Opcional. Usamos só para criar um Reveal cinematográfico e divertido nesse jogo privado.','photo_consent':'Aceito usar esta foto neste jogo privado.','custom_prompt':'✏️ Qual é a sua resposta?','custom_placeholder':'Escreva uma resposta curta, engraçada e verdadeira…','guess_board':'👀 O que todo mundo chutou?','score_continue':'Continuamos já já…',
 'lobby_game':'🎭 O jogo de vocês — todo mundo vê','topics_label':'Temas:','length_label':'Duração:','level_label':'Nível:','about_label':'Quem somos:','prize_label':'🏆 Prêmio:','lobby_note':'O anfitrião define a base. Cada jogador pode adicionar até 6 temas extras.','add_topics_note':'Cada jogador pode adicionar até 6 temas além dos escolhidos pelo anfitrião.','edit_game':'✏️ Editar jogo','edit_title':'✏️ Editar antes de começar','save_changes':'Salvar alterações','cancel':'Cancelar','rounds_word':'rodadas',
 'final_hero_generating':'🎬 Criando o pôster final da galera…','hero_generating_static':'✨ Criando um Reveal cinematográfico… o jogo continua normalmente.'
},
'fr':{
 'all_topics_selected':'Vous avez déjà choisi tous les thèmes disponibles 😄','max_topics':'Vous pouvez ajouter jusqu’à 6 thèmes','adult_topic_requires':'L’hôte doit confirmer une salle 18+ avant d’ajouter l’intimité','save_failed':'Impossible d’enregistrer','game_updated':'✓ Partie mise à jour pour tout le monde',
 'choose_image':'Choisissez une image','image_too_large':'Choisissez une image de moins de 12 Mo','preparing_image':'Préparation de la photo…','image_ready':'Photo prête à être enregistrée.','image_read_failed':'Impossible de lire cette image','choose_image_first':'Choisissez d’abord une photo','photo_consent_required':'Acceptez d’abord l’utilisation de la photo','room_connection_lost':'Connexion à la salle perdue — rejoignez à nouveau via le lien','saving':'Enregistrement…','uploading_photo':'Envoi de la photo…','photo_saved':'✓ Photo enregistrée','not_saved':'Non enregistré','save_photo':'Enregistrer la photo',
 'name_required':'Entrez votre prénom','joining':'Connexion…','retry_join':'Nouvel essai…','game_started':'La partie a déjà commencé','removed':'L’hôte a déjà continué sans vous','slow_server':'Le serveur met du temps — réessayez','join_failed':'Impossible de rejoindre','old_room_missing':'Cette ancienne salle n’existe plus — vous pouvez créer une nouvelle partie',
 'score_tied':'🔥 C’est serré ! Tout le monde peut encore gagner.','leader_one':'⚡ {name} mène d’un seul point !','leader_now':'🏆 {name} est en tête','photo_count':'📸 {done} joueurs sur {total} ont ajouté une photo. Pour les meilleurs Reveals, l’idéal est que tout le monde en ajoute une.','photo_ready':'✓ Ta photo est prête pour le Reveal','winner_prize':'🏆 {name} gagne le prix : {prize}',
 'final_ai_missing':'⚠️ Le poster AI n’était pas disponible cette fois. La partie s’est quand même terminée normalement.','ai_reveal_ready':'✨ AI REVEAL — nouvelle image créée pour cette manche','ai_reveal_generating':'✨ Création de votre AI Reveal… la partie peut continuer.','ai_image_missing':'⚠️ L’image AI n’a pas été créée cette fois — on continue.',
 'interactive_live':'⚡ Maintenant, ça sort de l’écran','match_yes':'🎯 MATCH ! +1 point chacun','match_no':'😄 Pas le même choix cette fois — on continue','secret_short':'Réponse courte — en secret','save_secret':'Enregistrer la réponse secrète','match_saved':'🔒 Ta réponse secrète est enregistrée','match_waiting':'👀 On attend les deux joueurs','match_wait_text':'Quand les deux auront répondu, on révélera le Match.','short_answer_required':'Écris une réponse courte','answer_saving':'✓ Enregistrement…','match_save_failed':'Impossible d’enregistrer la réponse du Match',
 'no_previous':'Il n’y a pas encore de manche précédente','back_game':'✕ Retour à la partie','previous_view':'Manche précédente — consultation seulement','answered':'{name} a répondu :','previous_note':'Tu peux revenir voir ici sans changer la partie ni le score.',
 'custom_short_required':'Écris une réponse courte','answer_received':'✓ Réponse reçue','saving_secret':'Enregistrement secret et mise à jour de la partie…','choice_received':'✓ Choix reçu','saving_update':'Enregistrement et mise à jour…','connection_slow':'La connexion est lente — réessaie','retry':'Réessayer',
 'back_lobby_ok':'Retour au lobby — vous pouvez inviter la personne qui manquait','reopen_too_late':'Il est trop tard pour revenir au lobby','replay_loading':'Préparation d’une nouvelle partie…','replay_new_questions':'Même groupe, nouvelles questions 🔥','replay_failed':'Impossible de relancer la partie',
 'duo_finishes':' — la partie se terminera avec le joueur restant','advanced_next':' — passage à la question suivante','need_two':'Il faut au moins deux joueurs pour continuer','remove_failed':'Impossible de retirer ce joueur',
 'starting':'⚡ Démarrage…','game_ready':'✓ Partie prête','start_failed':'Impossible de commencer — il faut au moins 2 joueurs','skipped_no_score':'Passée sans points','skip_failed':'Impossible de passer','wait_match_answers':'On attend les deux réponses du Match','wait_all_guesses':'On attend tous les pronostics',
 'photo_button':'📸 Ajouter / changer la photo','photo_title':'📸 Ta photo','photo_help':'Optionnel. Elle sert uniquement à créer un Reveal cinématographique amusant dans cette partie privée.','photo_consent':'J’accepte l’utilisation de cette photo dans cette partie privée.','custom_prompt':'✏️ Alors, ta réponse ?','custom_placeholder':'Écris une réponse courte, drôle et sincère…','guess_board':'👀 Qu’est-ce que tout le monde a deviné ?','score_continue':'On continue dans un instant…',
 'lobby_game':'🎭 Votre partie — visible par tous','topics_label':'Thèmes :','length_label':'Durée :','level_label':'Niveau :','about_label':'Qui sommes-nous :','prize_label':'🏆 Prix :','lobby_note':'L’hôte définit la base. Chaque joueur peut ajouter jusqu’à 6 thèmes supplémentaires.','add_topics_note':'Chaque joueur peut ajouter jusqu’à 6 thèmes en plus de ceux choisis par l’hôte.','edit_game':'✏️ Modifier la partie','edit_title':'✏️ Modifier avant de commencer','save_changes':'Enregistrer','cancel':'Annuler','rounds_word':'manches',
 'final_hero_generating':'🎬 Création du poster final du groupe…','hero_generating_static':'✨ Création d’un Reveal cinématographique… la partie continue normalement.'
},
'ja':{
 'all_topics_selected':'選べるテーマは全部選択済みです 😄','max_topics':'追加できるテーマは6個までです','adult_topic_requires':'親密なテーマを追加するには、ホストが18+ルームを確認してください','save_failed':'保存できませんでした','game_updated':'✓ 全員のゲーム設定を更新しました',
 'choose_image':'画像を選んでください','image_too_large':'12MB以下の画像を選んでください','preparing_image':'写真を準備中…','image_ready':'保存できる状態になりました。','image_read_failed':'画像を読み込めませんでした','choose_image_first':'先に写真を選んでください','photo_consent_required':'写真の使用に同意してください','room_connection_lost':'ルームとの接続が切れました — リンクから入り直してください','saving':'保存中…','uploading_photo':'写真をアップロード中…','photo_saved':'✓ 写真を保存しました','not_saved':'保存されませんでした','save_photo':'写真を保存',
 'name_required':'名前を入力してください','joining':'参加中…','retry_join':'もう一度試しています…','game_started':'ゲームはすでに始まっています','removed':'ホストはすでにあなた抜きでゲームを続けています','slow_server':'サーバーの応答が遅いです — もう一度試してください','join_failed':'参加できませんでした','old_room_missing':'そのルームはもうありません — 新しいゲームを作れます',
 'score_tied':'🔥 接戦！まだ誰にでもチャンスあり。','leader_one':'⚡ {name} が1点差でリード！','leader_now':'🏆 現在 {name} がリード','photo_count':'📸 {done}/{total}人が写真を追加しました。最高のRevealには全員の写真がおすすめです。','photo_ready':'✓ Reveal用の写真は準備OK','winner_prize':'🏆 {name} の勝ち！賞品：{prize}',
 'final_ai_missing':'⚠️ 今回はAIポスターを作れませんでした。ゲームは通常どおり終了しています。','ai_reveal_ready':'✨ AI REVEAL — このラウンド専用の新しい画像を作成しました','ai_reveal_generating':'✨ AI Revealを作成中…ゲームはそのまま続けられます。','ai_image_missing':'⚠️ 今回はAI画像を作れませんでした — ゲームを続けましょう。',
 'interactive_live':'⚡ ここからは画面の外へ','match_yes':'🎯 MATCH! 2人とも+1点','match_no':'😄 今回は一致せず — 次へ','secret_short':'短い答えを秘密で入力','save_secret':'秘密の答えを保存','match_saved':'🔒 秘密の答えを保存しました','match_waiting':'👀 2人の回答を待っています','match_wait_text':'2人とも答えたらMatchかどうか公開します。','short_answer_required':'短い答えを入力してください','answer_saving':'✓ 保存中…','match_save_failed':'Matchの答えを保存できませんでした',
 'no_previous':'まだ前のラウンドはありません','back_game':'✕ ゲームに戻る','previous_view':'前のラウンド — 閲覧のみ','answered':'{name} の答え：','previous_note':'ここを見てもゲームやスコアは変わりません。',
 'custom_short_required':'短い答えを入力してください','answer_received':'✓ 答えを受け付けました','saving_secret':'秘密で保存してゲームを更新中…','choice_received':'✓ 選択を受け付けました','saving_update':'保存してゲームを更新中…','connection_slow':'接続が遅いです — もう一度試してください','retry':'もう一度',
 'back_lobby_ok':'ロビーに戻りました — 足りないメンバーを招待できます','reopen_too_late':'もうロビーには戻れません','replay_loading':'新しいゲームを準備中…','replay_new_questions':'同じメンバー、新しい質問 🔥','replay_failed':'もう一度ゲームを始められませんでした',
 'duo_finishes':' — 残った1人でゲーム終了になります','advanced_next':' — 次の質問へ進みました','need_two':'続けるには2人以上必要です','remove_failed':'プレイヤーを外せませんでした',
 'starting':'⚡ スタート中…','game_ready':'✓ ゲーム準備OK','start_failed':'開始できません — 2人以上必要です','skipped_no_score':'得点なしでスキップしました','skip_failed':'スキップできませんでした','wait_match_answers':'Matchの2人の答えを待っています','wait_all_guesses':'全員の予想を待っています',
 'photo_button':'📸 写真を追加 / 変更','photo_title':'📸 あなたの写真','photo_help':'任意。プライベートゲーム内の楽しいシネマ風Revealを作るためだけに使います。','photo_consent':'この写真をこのプライベートゲームで使うことに同意します。','custom_prompt':'✏️ あなたの答えは？','custom_placeholder':'短くて、面白くて、本音の答えを…','guess_board':'👀 みんなの予想は？','score_continue':'もうすぐ続きます…',
 'lobby_game':'🎭 みんなに見えるゲーム設定','topics_label':'テーマ：','length_label':'長さ：','level_label':'レベル：','about_label':'メンバーについて：','prize_label':'🏆 賞品：','lobby_note':'ホストが基本を決め、各プレイヤーは追加テーマを6個まで選べます。','add_topics_note':'ホストが選んだもの以外に、各プレイヤーが6テーマまで追加できます。','edit_game':'✏️ ゲームを編集','edit_title':'✏️ 開始前にゲームを編集','save_changes':'変更を保存','cancel':'キャンセル','rounds_word':'ラウンド',
 'final_hero_generating':'🎬 グループの最終ポスターを作成中…','hero_generating_static':'✨ シネマ風Revealを作成中…ゲームは通常どおり続きます。'
},
'he':{
 'all_topics_selected':'כבר בחרתם את כל הנושאים הזמינים 😄','max_topics':'אפשר לבחור עד 6 נושאים','adult_topic_requires':'כדי להוסיף אינטימיות, המארח צריך לאשר חדר 18+','save_failed':'לא הצלחתי לשמור','game_updated':'✓ המשחק עודכן לכולם',
 'choose_image':'בחר תמונה','image_too_large':'בחר תמונה עד 12MB','preparing_image':'מכין את התמונה…','image_ready':'התמונה מוכנה לשמירה.','image_read_failed':'לא הצלחתי לקרוא את התמונה','choose_image_first':'בחר תמונה קודם','photo_consent_required':'צריך לאשר שימוש בתמונה','room_connection_lost':'החיבור לחדר אבד — היכנסו שוב מהלינק','saving':'שומר…','uploading_photo':'מעלה תמונה…','photo_saved':'✓ התמונה נשמרה','not_saved':'לא נשמרה','save_photo':'שמור תמונה',
 'name_required':'צריך שם','joining':'נכנס…','retry_join':'מנסה שוב…','game_started':'המשחק כבר התחיל','removed':'המארח כבר המשיך בלעדיך','slow_server':'השרת עדיין איטי — נסו שוב','join_failed':'לא הצלחתי להצטרף','old_room_missing':'החדר הישן כבר לא קיים — אפשר ליצור משחק חדש',
 'score_tied':'🔥 צמוד! הכול פתוח.','leader_one':'⚡ {name} מוביל/ה בנקודה אחת בלבד!','leader_now':'🏆 {name} מוביל/ה כרגע','photo_count':'📸 {done} מתוך {total} העלו תמונה. לתוצאות הוויזואליות הכי טובות כדאי שכולם יעלו.','photo_ready':'✓ יש לך תמונה מוכנה ל־Reveal','winner_prize':'🏆 {name} זכה/תה בפרס: {prize}',
 'final_ai_missing':'⚠️ פוסטר ה־AI לא נוצר הפעם. המשחק הסתיים כרגיל.','ai_reveal_ready':'✨ AI REVEAL — נוצרה תמונה חדשה במיוחד לסיבוב הזה','ai_reveal_generating':'✨ יוצר עכשיו AI Reveal מהתמונה שלכם…','ai_image_missing':'⚠️ תמונת ה־AI לא נוצרה הפעם — ממשיכים במשחק.',
 'interactive_live':'⚡ עכשיו זה יוצא מהמסך','match_yes':'🎯 MATCH! +1 נקודה לשניכם','match_no':'😄 לא אותו דבר הפעם — ממשיכים','secret_short':'תשובה קצרה — בסוד','save_secret':'שמור תשובה בסוד','match_saved':'🔒 התשובה שלך נשמרה','match_waiting':'👀 מחכים לשני השחקנים','match_wait_text':'כששניהם יענו נגלה אם יש MATCH.','short_answer_required':'כתבו תשובה קצרה','answer_saving':'✓ התשובה נשמרת…','match_save_failed':'לא הצלחתי לשמור את תשובת ה־Match',
 'no_previous':'עדיין אין סיבוב קודם','back_game':'✕ חזרה למשחק','previous_view':'סיבוב קודם — צפייה בלבד','answered':'{name} ענה/תה:','previous_note':'אפשר לחזור לכאן בלי לשנות את המשחק או את הניקוד.',
 'custom_short_required':'כתוב תשובה קצרה','answer_received':'✓ התשובה נקלטה','saving_secret':'שומר בסוד ומעדכן את המשחק…','choice_received':'✓ הבחירה נקלטה','saving_update':'שומר ומעדכן את המשחק…','connection_slow':'החיבור איטי — נסו שוב','retry':'נסה שוב',
 'back_lobby_ok':'חזרנו ללובי — אפשר לצרף את מי שחסר','reopen_too_late':'כבר מאוחר מדי לחזור ללובי','replay_loading':'מכין משחק חדש…','replay_new_questions':'אותה חבורה, שאלות חדשות 🔥','replay_failed':'לא הצלחתי לפתוח משחק חוזר',
 'duo_finishes':' — המשחק ייסגר עם המשתתף שנותר','advanced_next':' — עברנו לשאלה הבאה','need_two':'צריך לפחות שני שחקנים כדי להמשיך','remove_failed':'לא הצלחתי להסיר את השחקן',
 'starting':'⚡ מתחילים…','game_ready':'✓ המשחק מוכן','start_failed':'לא הצלחתי להתחיל — צריך לפחות 2 שחקנים','skipped_no_score':'דילגנו בלי ניקוד','skip_failed':'לא הצלחתי לדלג','wait_match_answers':'מחכים לשתי תשובות ה־Match','wait_all_guesses':'מחכים לכל הניחושים',
 'photo_button':'📸 הוסף/החלף תמונה','photo_title':'📸 התמונה שלך','photo_help':'אופציונלי. נשתמש בה רק כדי ליצור Reveal קולנועי מצחיק במהלך המשחק.','photo_consent':'אני מאשר/ת להשתמש בתמונה במשחק הפרטי הזה.','custom_prompt':'✏️ אז מה התשובה שלך?','custom_placeholder':'כתוב/י תשובה קצרה, מצחיקה ואמיתית…','guess_board':'👀 מה כולם ניחשו?','score_continue':'ממשיכים בעוד רגע…',
 'lobby_game':'🎭 המשחק שלכם — כולם רואים','topics_label':'נושאים:','length_label':'אורך:','level_label':'רמה:','about_label':'מי אנחנו:','prize_label':'🏆 פרס:','lobby_note':'המארח קובע את הבסיס — וכל משתתף יכול לבחור עד 6 נושאים שמעניינים אותו.','add_topics_note':'כאן כל שחקן יכול להוסיף עד 6 נושאים מעבר למה שהמארח כבר בחר.','edit_game':'✏️ עריכת המשחק','edit_title':'✏️ עריכת המשחק לפני שמתחילים','save_changes':'שמור שינויים','cancel':'ביטול','rounds_word':'סיבובים',
 'final_hero_generating':'🎬 מכין פוסטר סיום של החבורה…','hero_generating_static':'✨ יוצר Reveal קולנועי… המשחק ממשיך כרגיל.'
}
}
for _lang,_extra in POLISH_UI_EXTRA.items():
    if _lang in UI_COPY: UI_COPY[_lang].update(_extra)

LAST_RESORT = {
 'en':('What would surprise people who think they know {name} well?',['A spontaneous choice','The safe choice','Something nobody expects','It depends on the moment']),
 'es':('¿Qué sorprendería más a quienes creen conocer bien a {name}?',['Una elección impulsiva','La opción segura','Algo que nadie espera','Depende del momento']),
 'pt-BR':('O que mais surpreenderia quem acha que conhece {name} bem?',['Uma escolha impulsiva','A opção segura','Algo que ninguém espera','Depende do momento']),
 'fr':('Qu’est-ce qui surprendrait le plus ceux qui pensent bien connaître {name} ?',['Un choix spontané','Le choix rassurant','Un truc que personne n’attend','Ça dépend du moment']),
 'ja':('{name}をよく知ってるつもりの人が一番驚きそうなのは？',['勢いのある選択','無難な選択','誰も予想しないこと','その時次第']),
 'he':('מה הכי יפתיע את מי שחושב שהוא מכיר את {name} טוב?',['בחירה ספונטנית','בחירה בטוחה','משהו שאף אחד לא מצפה לו','תלוי במצב'])
}
def last_resort(lang,name):
    text,opts=LAST_RESORT[normalize_language(lang)]
    return text.format(name=name),list(opts)


STATIC_UI_EXTRA = {
'en':{'context_hint':'A few words are enough. The more we know, the more personal the game feels.','personalizing_note':'✨ The game uses your topics and group description to shape this game, then learns from answers as you play.','previous':'← Previous round','back_lobby':'↩️ Back to lobby','skip':'⏭️ Too personal / skip','photo_short':'📸 Photo','custom_save':'Save in secret','edit_topics':'Topics','edit_rounds':'Number of rounds','edit_spice':'Boldness level','edit_about':'About us','edit_prize':'🏆 Prize'},
'es':{'context_hint':'Con unas palabras basta. Cuanto más sepamos, más vuestra será la partida.','personalizing_note':'✨ El juego usa vuestros temas y descripción para preparar la partida y aprende de las respuestas mientras jugáis.','previous':'← Ronda anterior','back_lobby':'↩️ Volver al lobby','skip':'⏭️ Demasiado personal / saltar','photo_short':'📸 Foto','custom_save':'Guardar en secreto','edit_topics':'Temas','edit_rounds':'Número de rondas','edit_spice':'Nivel de atrevimiento','edit_about':'Quiénes somos','edit_prize':'🏆 Premio'},
'pt-BR':{'context_hint':'Poucas palavras já ajudam. Quanto mais contexto, mais a cara de vocês fica o jogo.','personalizing_note':'✨ O jogo usa os temas e a descrição da galera para montar a partida e aprende com as respostas enquanto vocês jogam.','previous':'← Rodada anterior','back_lobby':'↩️ Voltar ao lobby','skip':'⏭️ Pessoal demais / pular','photo_short':'📸 Foto','custom_save':'Salvar em segredo','edit_topics':'Temas','edit_rounds':'Número de rodadas','edit_spice':'Nível de ousadia','edit_about':'Quem somos','edit_prize':'🏆 Prêmio'},
'fr':{'context_hint':'Quelques mots suffisent. Plus on vous connaît, plus la partie vous ressemble.','personalizing_note':'✨ Le jeu utilise vos thèmes et votre description pour préparer la partie, puis apprend de vos réponses au fil des manches.','previous':'← Manche précédente','back_lobby':'↩️ Retour au lobby','skip':'⏭️ Trop perso / passer','photo_short':'📸 Photo','custom_save':'Enregistrer en secret','edit_topics':'Thèmes','edit_rounds':'Nombre de manches','edit_spice':'Niveau d’audace','edit_about':'Qui sommes-nous','edit_prize':'🏆 Prix'},
'ja':{'context_hint':'少し書くだけでOK。情報が多いほど、みんならしいゲームになります。','personalizing_note':'✨ 選んだテーマとグループ紹介を使ってゲームを作り、プレイ中の回答からさらに学びます。','previous':'← 前のラウンド','back_lobby':'↩️ ロビーに戻る','skip':'⏭️ 個人的すぎる / スキップ','photo_short':'📸 写真','custom_save':'秘密で保存','edit_topics':'テーマ','edit_rounds':'ラウンド数','edit_spice':'攻め度','edit_about':'メンバーについて','edit_prize':'🏆 賞品'},
'he':{'context_hint':'כמה מילים מספיקות. ככל שנכיר אתכם יותר, המשחק יהיה יותר שלכם.','personalizing_note':'✨ המשחק ישתמש בנושאים ובתיאור שלכם כדי להכין שאלות לערב הזה, ובהמשך גם בתשובות מהסיבובים הקודמים.','previous':'← סיבוב קודם','back_lobby':'↩️ חזרה ללובי','skip':'⏭️ אישי מדי / דלג','photo_short':'📸 תמונה','custom_save':'שמור בסוד','edit_topics':'נושאים','edit_rounds':'מספר סיבובים','edit_spice':'רמת חריפות','edit_about':'מי אנחנו','edit_prize':'🏆 פרס'}
}
for _lang,_extra in STATIC_UI_EXTRA.items():
    if _lang in UI_COPY: UI_COPY[_lang].update(_extra)

LOCK_EXTRA = {
'en':{'language_locked':'The host chose the language for this room.','left_game':'left the game'},
'es':{'language_locked':'El anfitrión eligió el idioma de esta sala.','left_game':'salió de la partida'},
'pt-BR':{'language_locked':'O anfitrião escolheu o idioma desta sala.','left_game':'saiu do jogo'},
'fr':{'language_locked':'L’hôte a choisi la langue de cette salle.','left_game':'a quitté la partie'},
'ja':{'language_locked':'このルームの言語はホストが設定しています。','left_game':'ゲーム退出'},
'he':{'language_locked':'המארח בחר את השפה של החדר הזה.','left_game':'יצא/ה מהמשחק'}
}
for _lang,_extra in LOCK_EXTRA.items():
    if _lang in UI_COPY: UI_COPY[_lang].update(_extra)

# Presentation-only additions for the Cream + Purple interface.
POLISH_COPY = {'en': {'gender_label': 'Gender (optional)', 'gender_male': 'Male', 'gender_female': 'Female', 'gender_unspecified': 'Prefer not to say', 'profile_label': 'My profile', 'players_scores': 'Players & scores', 'instant_loading': 'Preparing Visual Reveal…', 'reconnecting': 'Reconnecting… your place is saved.', 'retry_connection': 'Try again', 'return_room': 'Return to room'}, 'he': {'gender_label': 'מגדר (לא חובה)', 'gender_male': 'גבר', 'gender_female': 'אישה', 'gender_unspecified': 'מעדיפ/ה לא לציין', 'profile_label': 'הפרופיל שלי', 'players_scores': 'שחקנים וניקוד', 'instant_loading': 'מכינים Visual Reveal…', 'reconnecting': 'מתחברים מחדש… המקום שלך נשמר.', 'retry_connection': 'ניסיון נוסף', 'return_room': 'חזרה לחדר'}, 'es': {'gender_label': 'Género (opcional)', 'gender_male': 'Hombre', 'gender_female': 'Mujer', 'gender_unspecified': 'Prefiero no decirlo', 'profile_label': 'Mi perfil', 'players_scores': 'Jugadores y puntos', 'instant_loading': 'Preparando Visual Reveal…', 'reconnecting': 'Reconectando… tu lugar está guardado.', 'retry_connection': 'Reintentar', 'return_room': 'Volver a la sala'}, 'pt-BR': {'gender_label': 'Gênero (opcional)', 'gender_male': 'Homem', 'gender_female': 'Mulher', 'gender_unspecified': 'Prefiro não informar', 'profile_label': 'Meu perfil', 'players_scores': 'Jogadores e pontos', 'instant_loading': 'Preparando Visual Reveal…', 'reconnecting': 'Reconectando… seu lugar está salvo.', 'retry_connection': 'Tentar novamente', 'return_room': 'Voltar à sala'}, 'fr': {'gender_label': 'Genre (facultatif)', 'gender_male': 'Homme', 'gender_female': 'Femme', 'gender_unspecified': 'Préfère ne pas répondre', 'profile_label': 'Mon profil', 'players_scores': 'Joueurs et scores', 'instant_loading': 'Préparation du Visual Reveal…', 'reconnecting': 'Reconnexion… votre place est conservée.', 'retry_connection': 'Réessayer', 'return_room': 'Retour à la salle'}, 'ja': {'gender_label': '性別（任意）', 'gender_male': '男性', 'gender_female': '女性', 'gender_unspecified': '回答しない', 'profile_label': 'プロフィール', 'players_scores': 'プレイヤーと得点', 'instant_loading': 'Visual Reveal を準備中…', 'reconnecting': '再接続中…参加情報は保存されています。', 'retry_connection': '再試行', 'return_room': 'ルームに戻る'}}
for _lang,_extra in POLISH_COPY.items():
    UI_COPY[_lang].update(_extra)
