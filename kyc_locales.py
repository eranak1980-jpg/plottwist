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
