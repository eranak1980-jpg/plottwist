(function(){
const LANGS=[
 ['en','English'],['es','Español'],['pt-BR','Português (Brasil)'],
 ['fr','Français'],['ja','日本語'],['he','עברית']
];
const TOPICS={
'מה היית עושה אם…':{en:'What would you do if…',es:'¿Qué harías si…?', 'pt-BR':'O que você faria se…',fr:'Que ferais-tu si…',ja:'もし〜だったら？',he:'מה היית עושה אם…'},
'דילמות':{en:'Dilemmas',es:'Dilemas','pt-BR':'Dilemas',fr:'Dilemmes',ja:'究極の選択',he:'דילמות'},
'מי הכי…':{en:'Who is most likely…',es:'Quién es más probable…','pt-BR':'Quem é mais provável…',fr:'Qui est le plus susceptible…',ja:'一番ありそうなのは誰？',he:'מי הכי…'},
'מביך אבל מצחיק':{en:'Awkward but funny',es:'Vergonzoso pero gracioso','pt-BR':'Vergonha alheia, mas engraçado',fr:'Gênant mais drôle',ja:'恥ずかしいけど笑える',he:'מביך אבל מצחיק'},
'סודות והרגלים':{en:'Secrets & habits',es:'Secretos y hábitos','pt-BR':'Segredos e hábitos',fr:'Secrets & habitudes',ja:'秘密とクセ',he:'סודות והרגלים'},
'משפחה':{en:'Family',es:'Familia','pt-BR':'Família',fr:'Famille',ja:'家族',he:'משפחה'},
'חברות ואמון':{en:'Friendship & trust',es:'Amistad y confianza','pt-BR':'Amizade e confiança',fr:'Amitié & confiance',ja:'友情と信頼',he:'חברות ואמון'},
'דייטים':{en:'Dating',es:'Citas','pt-BR':'Encontros',fr:'Dating',ja:'デート',he:'דייטים'},
'טיולים וחופשות':{en:'Travel & vacations',es:'Viajes y vacaciones','pt-BR':'Viagens e férias',fr:'Voyages & vacances',ja:'旅行・休暇',he:'טיולים וחופשות'},
'כסף מטורף':{en:'Crazy money',es:'Dinero loco','pt-BR':'Dinheiro sem limite',fr:'Argent fou',ja:'もし大金があったら',he:'כסף מטורף'},
'חלומות ופנטזיות':{en:'Dreams & fantasies',es:'Sueños y fantasías','pt-BR':'Sonhos e fantasias',fr:'Rêves & fantasmes',ja:'夢と妄想',he:'חלומות ופנטזיות'},
'גייז / LGBTQ+':{en:'LGBTQ+',es:'LGBTQ+','pt-BR':'LGBTQ+',fr:'LGBTQ+',ja:'LGBTQ+',he:'גייז / LGBTQ+'},
'זוגיות':{en:'Relationships',es:'Parejas','pt-BR':'Relacionamentos',fr:'Couples',ja:'恋愛・カップル',he:'זוגיות'},
'חיי לילה':{en:'Nightlife',es:'Vida nocturna','pt-BR':'Vida noturna',fr:'Vie nocturne',ja:'ナイトライフ',he:'חיי לילה'},
'נסיעות':{en:'Travel',es:'Viajes','pt-BR':'Viagens',fr:'Voyages',ja:'旅',he:'נסיעות'},
'כסף':{en:'Money',es:'Dinero','pt-BR':'Dinheiro',fr:'Argent',ja:'お金',he:'כסף'},
'קריירה ועסקים':{en:'Career & business',es:'Carrera y negocios','pt-BR':'Carreira e negócios',fr:'Carrière & business',ja:'仕事・キャリア',he:'קריירה ועסקים'},
'רשתות חברתיות':{en:'Social media',es:'Redes sociales','pt-BR':'Redes sociais',fr:'Réseaux sociaux',ja:'SNS',he:'רשתות חברתיות'},
'נוסטלגיה':{en:'Nostalgia',es:'Nostalgia','pt-BR':'Nostalgia',fr:'Nostalgie',ja:'懐かしさ',he:'נוסטלגיה'},
'אוכל':{en:'Food',es:'Comida','pt-BR':'Comida',fr:'Food',ja:'食べ物',he:'אוכל'},
'מוזיקה':{en:'Music',es:'Música','pt-BR':'Música',fr:'Musique',ja:'音楽',he:'מוזיקה'},
'הרפתקאות':{en:'Adventures',es:'Aventuras','pt-BR':'Aventuras',fr:'Aventures',ja:'冒険',he:'הרפתקאות'},
'אישיות':{en:'Personality',es:'Personalidad','pt-BR':'Personalidade',fr:'Personnalité',ja:'性格',he:'אישיות'},
'טכנולוגיה':{en:'Technology',es:'Tecnología','pt-BR':'Tecnologia',fr:'Technologie',ja:'テクノロジー',he:'טכנולוגיה'},
'ספורט וכושר':{en:'Sports & fitness',es:'Deporte y fitness','pt-BR':'Esporte e fitness',fr:'Sport & fitness',ja:'スポーツ・フィットネス',he:'ספורט וכושר'},
'תרבות ופופ':{en:'Pop culture',es:'Cultura pop','pt-BR':'Cultura pop',fr:'Pop culture',ja:'ポップカルチャー',he:'תרבות ופופ'},
'אינטימיות למבוגרים':{en:'Adult / Intimacy (18+)',es:'Adultos / Intimidad (18+)','pt-BR':'Adulto / Intimidade (18+)',fr:'Adulte / Intimité (18+)',ja:'大人向け / 親密さ (18+)',he:'אינטימיות למבוגרים'}
};

const STATIC={
'מי באמת':{en:'Who really',es:'¿Quién de verdad','pt-BR':'Quem realmente',fr:'Qui connaît vraiment',ja:'本当に',he:'מי באמת'},
'מכיר את החבורה?':{en:'knows the crew?',es:'conoce al grupo?', 'pt-BR':'conhece a galera?',fr:'le groupe ?',ja:'仲間を知ってる？',he:'מכיר את החבורה?'},
'אחד עונה בסוד. כולם מנחשים. המשחק לומד אתכם תוך כדי.':{en:'One answers in secret. Everyone else guesses. The game learns your crew as you play.',es:'Uno responde en secreto. Los demás adivinan. El juego aprende cómo es vuestro grupo.', 'pt-BR':'Uma pessoa responde em segredo. O resto tenta adivinhar. O jogo aprende a galera enquanto vocês jogam.',fr:'Une personne répond en secret. Les autres devinent. Le jeu apprend à connaître votre groupe.',ja:'1人が秘密で答え、みんなが予想。遊ぶほど仲間のことがゲームに反映されます。',he:'אחד עונה בסוד. כולם מנחשים. המשחק לומד אתכם תוך כדי.'},
'איך משחקים?':{en:'How to play?',es:'¿Cómo se juega?','pt-BR':'Como jogar?',fr:'Comment jouer ?',ja:'遊び方',he:'איך משחקים?'},
'צור משחק':{en:'Create game',es:'Crear partida','pt-BR':'Criar jogo',fr:'Créer une partie',ja:'ゲームを作る',he:'צור משחק'},
'הצטרף למשחק':{en:'Join game',es:'Unirse a la partida','pt-BR':'Entrar no jogo',fr:'Rejoindre',ja:'ゲームに参加',he:'הצטרף למשחק'},
'איזה ערב בא לכם?':{en:'What kind of night are you having?',es:'¿Qué tipo de noche queréis?','pt-BR':'Que tipo de noite vocês querem?',fr:'Quelle soirée vous tente ?',ja:'どんな夜にする？',he:'איזה ערב בא לכם?'},
'על מה בא לכם לשחק?':{en:'What do you want to play about?',es:'¿Sobre qué queréis jugar?','pt-BR':'Sobre o que vocês querem jogar?',fr:'Sur quoi voulez-vous jouer ?',ja:'どんなテーマで遊ぶ？',he:'על מה בא לכם לשחק?'},
'עוד נושאים +':{en:'More topics +',es:'Más temas +','pt-BR':'Mais temas +',fr:'Plus de thèmes +',ja:'もっと見る +',he:'עוד נושאים +'},
'פחות נושאים −':{en:'Fewer topics −',es:'Menos temas −','pt-BR':'Menos temas −',fr:'Moins de thèmes −',ja:'閉じる −',he:'פחות נושאים −'},
'🎮 כמה סיבובים?':{en:'🎮 How many rounds?',es:'🎮 ¿Cuántas rondas?','pt-BR':'🎮 Quantas rodadas?',fr:'🎮 Combien de manches ?',ja:'🎮 何ラウンド？',he:'🎮 כמה סיבובים?'},
'🌶️ רמת החריפות':{en:'🌶️ Intensity',es:'🌶️ Intensidad','pt-BR':'🌶️ Intensidade',fr:'🌶️ Intensité',ja:'🌶️ 刺激度',he:'🌶️ רמת החריפות'},
'🏆 פרס למנצח':{en:'🏆 Winner prize',es:'🏆 Premio','pt-BR':'🏆 Prêmio',fr:'🏆 Prix du gagnant',ja:'🏆 勝者への賞品',he:'🏆 פרס למנצח'},
'(אופציונלי)':{en:'(optional)',es:'(opcional)','pt-BR':'(opcional)',fr:'(optionnel)',ja:'（任意）',he:'(אופציונלי)'},
'✨ ספרו ל־PlotTwist מי אתם':{en:'✨ Tell PlotTwist about your crew',es:'✨ Contadle a PlotTwist quiénes sois','pt-BR':'✨ Conte ao PlotTwist quem vocês são',fr:'✨ Dites à PlotTwist qui vous êtes',ja:'✨ みんなのことをPlotTwistに教えて',he:'✨ ספרו ל־PlotTwist מי אתם'},
'✨ בנה לי תיאור':{en:'✨ Build my description',es:'✨ Crear descripción','pt-BR':'✨ Criar descrição',fr:'✨ Créer ma description',ja:'✨ 説明を作る',he:'✨ בנה לי תיאור'},
'הצג דוגמאות ▾':{en:'Show examples ▾',es:'Ver ejemplos ▾','pt-BR':'Ver exemplos ▾',fr:'Voir des exemples ▾',ja:'例を見る ▾',he:'הצג דוגמאות ▾'},
'צור חדר':{en:'Create room',es:'Crear sala','pt-BR':'Criar sala',fr:'Créer la salle',ja:'ルームを作る',he:'צור חדר'},
'נכנסים לחבורה':{en:'Join the crew',es:'Entrar al grupo','pt-BR':'Entrar na galera',fr:'Rejoindre le groupe',ja:'仲間に参加',he:'נכנסים לחבורה'},
'הצטרף':{en:'Join',es:'Entrar','pt-BR':'Entrar',fr:'Rejoindre',ja:'参加',he:'הצטרף'},
'שתף לינק':{en:'Share link',es:'Compartir enlace','pt-BR':'Compartilhar link',fr:'Partager le lien',ja:'リンクを共有',he:'שתף לינק'},
'נושאים:':{en:'Topics:',es:'Temas:','pt-BR':'Temas:',fr:'Thèmes :',ja:'テーマ：',he:'נושאים:'},
'אורך:':{en:'Length:',es:'Duración:','pt-BR':'Duração:',fr:'Durée :',ja:'長さ：',he:'אורך:'},
'סיבובים':{en:'rounds',es:'rondas','pt-BR':'rodadas',fr:'manches',ja:'ラウンド',he:'סיבובים'},
'רמה:':{en:'Level:',es:'Nivel:','pt-BR':'Nível:',fr:'Niveau :',ja:'レベル：',he:'רמה:'},
'מי אנחנו:':{en:'About us:',es:'Quiénes somos:','pt-BR':'Quem somos:',fr:'Qui sommes-nous :',ja:'グループ紹介：',he:'מי אנחנו:'},
'🏆 פרס:':{en:'🏆 Prize:',es:'🏆 Premio:','pt-BR':'🏆 Prêmio:',fr:'🏆 Prix :',ja:'🏆 賞品：',he:'🏆 פרס:'},
'➕ רוצים להוסיף עוד משהו?':{en:'➕ Want to add something?',es:'➕ ¿Queréis añadir algo?','pt-BR':'➕ Querem adicionar algo?',fr:'➕ Ajouter quelque chose ?',ja:'➕ 追加したいテーマは？',he:'➕ רוצים להוסיף עוד משהו?'},
'✏️ עריכת המשחק':{en:'✏️ Edit game',es:'✏️ Editar partida','pt-BR':'✏️ Editar jogo',fr:'✏️ Modifier la partie',ja:'✏️ ゲームを編集',he:'✏️ עריכת המשחק'},
'✏️ עריכת המשחק לפני שמתחילים':{en:'✏️ Edit game before starting',es:'✏️ Editar antes de empezar','pt-BR':'✏️ Editar antes de começar',fr:'✏️ Modifier avant de commencer',ja:'✏️ 開始前に編集',he:'✏️ עריכת המשחק לפני שמתחילים'},
'נושאים':{en:'Topics',es:'Temas','pt-BR':'Temas',fr:'Thèmes',ja:'テーマ',he:'נושאים'},
'מספר סיבובים':{en:'Number of rounds',es:'Número de rondas','pt-BR':'Número de rodadas',fr:'Nombre de manches',ja:'ラウンド数',he:'מספר סיבובים'},
'רמת חריפות':{en:'Intensity',es:'Intensidad','pt-BR':'Intensidade',fr:'Intensité',ja:'刺激度',he:'רמת חריפות'},
'שמור שינויים':{en:'Save changes',es:'Guardar cambios','pt-BR':'Salvar alterações',fr:'Enregistrer',ja:'変更を保存',he:'שמור שינויים'},
'ביטול':{en:'Cancel',es:'Cancelar','pt-BR':'Cancelar',fr:'Annuler',ja:'キャンセル',he:'ביטול'},
'📸 הוסף/החלף תמונה':{en:'📸 Add/change photo',es:'📸 Añadir/cambiar foto','pt-BR':'📸 Adicionar/trocar foto',fr:'📸 Ajouter/changer la photo',ja:'📸 写真を追加・変更',he:'📸 הוסף/החלף תמונה'},
'📸 התמונה שלך':{en:'📸 Your photo',es:'📸 Tu foto','pt-BR':'📸 Sua foto',fr:'📸 Votre photo',ja:'📸 あなたの写真',he:'📸 התמונה שלך'},
'שמור תמונה':{en:'Save photo',es:'Guardar foto','pt-BR':'Salvar foto',fr:'Enregistrer la photo',ja:'写真を保存',he:'שמור תמונה'},
'✏️ אז מה התשובה שלך?':{en:'✏️ So what is your answer?',es:'✏️ ¿Cuál es tu respuesta?','pt-BR':'✏️ Qual é a sua resposta?',fr:'✏️ Alors, votre réponse ?',ja:'✏️ あなたの答えは？',he:'✏️ אז מה התשובה שלך?'},
'שמור בסוד':{en:'Save secretly',es:'Guardar en secreto','pt-BR':'Salvar em segredo',fr:'Enregistrer en secret',ja:'秘密で保存',he:'שמור בסוד'},
'← סיבוב קודם':{en:'← Previous round',es:'← Ronda anterior','pt-BR':'← Rodada anterior',fr:'← Manche précédente',ja:'← 前のラウンド',he:'← סיבוב קודם'},
'↩️ חזרה ללובי':{en:'↩️ Back to lobby',es:'↩️ Volver al lobby','pt-BR':'↩️ Voltar ao lobby',fr:'↩️ Retour au lobby',ja:'↩️ ロビーに戻る',he:'↩️ חזרה ללובי'},
'📸 תמונה':{en:'📸 Photo',es:'📸 Foto','pt-BR':'📸 Foto',fr:'📸 Photo',ja:'📸 写真',he:'📸 תמונה'},
'⏭️ אישי מדי / דלג':{en:'⏭️ Too personal / skip',es:'⏭️ Muy personal / saltar','pt-BR':'⏭️ Pessoal demais / pular',fr:'⏭️ Trop perso / passer',ja:'⏭️ 答えにくい / スキップ',he:'⏭️ אישי מדי / דלג'},
'👀 מה כולם ניחשו?':{en:'👀 What did everyone guess?',es:'👀 ¿Qué adivinó cada uno?','pt-BR':'👀 O que todo mundo chutou?',fr:'👀 Qu’ont deviné les autres ?',ja:'👀 みんなの予想は？',he:'👀 מה כולם ניחשו?'},
'לשאלה הבאה →':{en:'Next question →',es:'Siguiente pregunta →','pt-BR':'Próxima pergunta →',fr:'Question suivante →',ja:'次の質問 →',he:'לשאלה הבאה →'},
'מי מכיר את החבורה הכי טוב?':{en:'Who knows the crew best?',es:'¿Quién conoce mejor al grupo?','pt-BR':'Quem conhece melhor a galera?',fr:'Qui connaît le mieux le groupe ?',ja:'仲間を一番知っているのは誰？',he:'מי מכיר את החבורה הכי טוב?'},
'🔁 עוד משחק עם אותה חבורה':{en:'🔁 Play again with the same crew',es:'🔁 Otra partida con el mismo grupo','pt-BR':'🔁 Jogar de novo com a mesma galera',fr:'🔁 Rejouer avec le même groupe',ja:'🔁 同じメンバーでもう一度',he:'🔁 עוד משחק עם אותה חבורה'},
'משחק חדש':{en:'New game',es:'Nueva partida','pt-BR':'Novo jogo',fr:'Nouvelle partie',ja:'新しいゲーム',he:'משחק חדש'},
'הבנתי — יאללה משחקים':{en:'Got it — start playing',es:'Entendido — a jugar','pt-BR':'Entendi — vamos jogar',fr:'Compris — on joue',ja:'わかった — スタート',he:'הבנתי — יאללה משחקים'},
'ממשיכים בעוד רגע…':{en:'Continuing in a moment…',es:'Seguimos en un momento…','pt-BR':'Continuamos em instantes…',fr:'On continue dans un instant…',ja:'まもなく続きます…',he:'ממשיכים בעוד רגע…'}
};

const UI={
en:{saved_answer:'🔒 Answer saved',saved_guess:'✓ Guess saved',waiting_host:'⏳ Waiting for the host to start',start:'Start',starting:'⚡ Starting…',next:'Next question →',finish:'Finish & see winner 🏆',offline:'Offline',remove:'Remove',continue_without:'Continue without {name}',joined:'Joining…',retry_join:'Trying again…',join_failed:'Could not join',room_gone:'That old room no longer exists — you can start a new game',wait_subject:'Waiting for {name} to answer secretly…',wait_others:'Waiting for the other players…',wait_guesses:'Waiting for guesses from {names}…',score_one:'point',score_many:'points',correct:'🎯 Correct! +1 point',not_this_time:'Not this time',back_lobby:'Back in the lobby — invite whoever was missing',play_again:'Same crew, new questions 🔥',adult:'All players must be 18+ for adult content.',share:'Let’s see who really knows the crew',photo_saved:'✓ Photo saved',match_saved:'🔒 Your answer is saved',match_wait:'👀 Waiting for both players',match_no:'😄 Not a match this time — keep going',match_yes:'🎯 MATCH! +1 point each'},
es:{saved_answer:'🔒 Respuesta guardada',saved_guess:'✓ Predicción guardada',waiting_host:'⏳ Esperando a que el anfitrión empiece',start:'Empezar',starting:'⚡ Empezando…',next:'Siguiente pregunta →',finish:'Finalizar y ver ganador 🏆',offline:'Sin conexión',remove:'Eliminar',continue_without:'Continuar sin {name}',joined:'Entrando…',retry_join:'Intentando otra vez…',join_failed:'No se pudo entrar',room_gone:'Esa sala ya no existe — puedes crear una nueva',wait_subject:'Esperando a que {name} responda en secreto…',wait_others:'Esperando al resto…',wait_guesses:'Esperando las predicciones de {names}…',score_one:'punto',score_many:'puntos',correct:'🎯 ¡Acertaste! +1 punto',not_this_time:'Esta vez no',back_lobby:'Volvimos al lobby — podéis invitar a quien faltaba',play_again:'Mismo grupo, preguntas nuevas 🔥',adult:'Todos los jugadores deben tener 18+ para contenido adulto.',share:'A ver quién conoce de verdad al grupo',photo_saved:'✓ Foto guardada',match_saved:'🔒 Tu respuesta está guardada',match_wait:'👀 Esperando a los dos jugadores',match_no:'😄 No hubo match esta vez — seguimos',match_yes:'🎯 MATCH! +1 punto para cada uno'},
'pt-BR':{saved_answer:'🔒 Resposta salva',saved_guess:'✓ Palpite salvo',waiting_host:'⏳ Esperando o host começar',start:'Começar',starting:'⚡ Começando…',next:'Próxima pergunta →',finish:'Finalizar e ver vencedor 🏆',offline:'Offline',remove:'Remover',continue_without:'Continuar sem {name}',joined:'Entrando…',retry_join:'Tentando de novo…',join_failed:'Não foi possível entrar',room_gone:'Essa sala antiga não existe mais — crie um novo jogo',wait_subject:'Esperando {name} responder em segredo…',wait_others:'Esperando os outros jogadores…',wait_guesses:'Esperando os palpites de {names}…',score_one:'ponto',score_many:'pontos',correct:'🎯 Acertou! +1 ponto',not_this_time:'Dessa vez não',back_lobby:'Voltamos ao lobby — convide quem faltou',play_again:'Mesma galera, perguntas novas 🔥',adult:'Todos precisam ter 18+ para conteúdo adulto.',share:'Vamos ver quem realmente conhece a galera',photo_saved:'✓ Foto salva',match_saved:'🔒 Sua resposta foi salva',match_wait:'👀 Esperando os dois jogadores',match_no:'😄 Não deu match — seguimos',match_yes:'🎯 MATCH! +1 ponto para cada'},
fr:{saved_answer:'🔒 Réponse enregistrée',saved_guess:'✓ Pronostic enregistré',waiting_host:'⏳ En attente du lancement par l’hôte',start:'Commencer',starting:'⚡ Démarrage…',next:'Question suivante →',finish:'Finir et voir le gagnant 🏆',offline:'Hors ligne',remove:'Retirer',continue_without:'Continuer sans {name}',joined:'Connexion…',retry_join:'Nouvel essai…',join_failed:'Impossible de rejoindre',room_gone:'Cette ancienne salle n’existe plus — vous pouvez créer une nouvelle partie',wait_subject:'En attente de la réponse secrète de {name}…',wait_others:'En attente des autres joueurs…',wait_guesses:'En attente des pronostics de {names}…',score_one:'point',score_many:'points',correct:'🎯 Bien vu ! +1 point',not_this_time:'Pas cette fois',back_lobby:'Retour au lobby — invitez la personne qui manquait',play_again:'Même groupe, nouvelles questions 🔥',adult:'Tous les joueurs doivent avoir 18+ pour le contenu adulte.',share:'Voyons qui connaît vraiment le groupe',photo_saved:'✓ Photo enregistrée',match_saved:'🔒 Votre réponse est enregistrée',match_wait:'👀 En attente des deux joueurs',match_no:'😄 Pas de match cette fois — on continue',match_yes:'🎯 MATCH ! +1 point chacun'},
ja:{saved_answer:'🔒 回答を保存しました',saved_guess:'✓ 予想を保存しました',waiting_host:'⏳ ホストの開始を待っています',start:'スタート',starting:'⚡ 開始中…',next:'次の質問 →',finish:'終了して勝者を見る 🏆',offline:'オフライン',remove:'削除',continue_without:'{name}抜きで続ける',joined:'参加中…',retry_join:'もう一度試しています…',join_failed:'参加できませんでした',room_gone:'前のルームはもうありません — 新しいゲームを作れます',wait_subject:'{name}の秘密の回答を待っています…',wait_others:'他のプレイヤーを待っています…',wait_guesses:'{names}の予想を待っています…',score_one:'ポイント',score_many:'ポイント',correct:'🎯 正解！+1ポイント',not_this_time:'今回はハズレ',back_lobby:'ロビーに戻りました — 足りないメンバーを招待できます',play_again:'同じメンバー、新しい質問 🔥',adult:'大人向けコンテンツは全員18歳以上である必要があります。',share:'誰が一番みんなを知っているか試そう',photo_saved:'✓ 写真を保存しました',match_saved:'🔒 回答を保存しました',match_wait:'👀 2人の回答を待っています',match_no:'😄 今回は一致なし — 続けます',match_yes:'🎯 MATCH！2人とも+1ポイント'},
he:{saved_answer:'🔒 התשובה נשמרה',saved_guess:'✓ הניחוש נשמר',waiting_host:'⏳ מחכים למארח להתחיל את המשחק',start:'מתחילים',starting:'⚡ מתחילים…',next:'לשאלה הבאה →',finish:'לסיום ולמנצח 🏆',offline:'מנותק/ת',remove:'הסר/י',continue_without:'המשך בלי {name}',joined:'נכנס…',retry_join:'מנסה שוב…',join_failed:'לא הצלחתי להצטרף',room_gone:'החדר הישן כבר לא קיים — אפשר ליצור משחק חדש',wait_subject:'מחכים ל־{name} לענות בסוד…',wait_others:'מחכים לשאר השחקנים…',wait_guesses:'מחכים לניחושים של {names}…',score_one:'נק׳',score_many:'נק׳',correct:'🎯 קלעת! +1 נקודה',not_this_time:'לא הפעם',back_lobby:'חזרנו ללובי — אפשר לצרף את מי שחסר',play_again:'אותה חבורה, שאלות חדשות 🔥',adult:'צריך לאשר שכל המשתתפים בני 18 ומעלה',share:'בואו נראה מי באמת מכיר את החבורה',photo_saved:'✓ התמונה נשמרה',match_saved:'🔒 התשובה שלך נשמרה',match_wait:'👀 מחכים לשני השחקנים',match_no:'😄 לא אותו דבר הפעם — ממשיכים',match_yes:'🎯 MATCH! +1 נקודה לשניכם'}
};

const VIBES={
en:['Known each other for years','LGBTQ+ friends','Singles','Couples','Work friends','Travel lovers','Nightlife','Dating','Dating apps','Sarcastic','Competitive','Open about everything','Want a funny night','Want a bold night'],
es:['Amigos de hace años','Amigos LGBTQ+','Solteros','Parejas','Compañeros de trabajo','Viajeros','Vida nocturna','Citas','Apps de citas','Sarcásticos','Competitivos','Hablan de todo','Noche divertida','Noche atrevida'],
'pt-BR':['Amigos há anos','Amigos LGBTQ+','Solteiros','Casais','Amigos do trabalho','Amam viajar','Vida noturna','Encontros','Apps de namoro','Sarcásticos','Competitivos','Falam de tudo','Noite divertida','Noite ousada'],
fr:['Amis depuis des années','Amis LGBTQ+','Célibataires','Couples','Collègues','Fans de voyage','Vie nocturne','Dating','Applis de rencontre','Sarcastiques','Compétitifs','Parlent de tout','Soirée drôle','Soirée audacieuse'],
ja:['長年の友達','LGBTQ+の友達','シングル','カップル','仕事仲間','旅行好き','夜遊び好き','デート','マッチングアプリ','皮肉好き','負けず嫌い','何でも話す','笑える夜にしたい','ちょっと攻めたい'],
he:['מכירים שנים','חברים גייז','רווקים','זוגות','חברים מהעבודה','אוהבים לטייל','חיי לילה','דייטים','אפליקציות היכרויות','ציניים','תחרותיים','פתוחים לדבר על הכול','רוצים ערב מצחיק','רוצים ערב חצוף']
};

const originalNodes=new WeakMap(), originalAttrs=new WeakMap();
function lang(){let x=localStorage.getItem('plot_ui_language')||'en';return LANGS.some(v=>v[0]===x)?x:'en'}
function trStatic(src,l=lang()){let x=STATIC[src];return x?(x[l]||x.en||src):src}
function t(key,vars={},l=lang()){let pack=UI[l]||UI.en,x=pack[key]||UI.en[key]||key;Object.keys(vars).forEach(k=>x=x.replaceAll('{'+k+'}',String(vars[k])));return x}
function topic(key,l=lang()){return TOPICS[key]?(TOPICS[key][l]||TOPICS[key].en||key):key}
function apply(root=document,l=lang()){
 document.documentElement.lang=l;document.documentElement.dir=l==='he'?'rtl':'ltr';
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 let n;while(n=walker.nextNode()){if(n.parentElement&&['SCRIPT','STYLE','OPTION'].includes(n.parentElement.tagName))continue;if(!originalNodes.has(n))originalNodes.set(n,n.nodeValue);let raw=originalNodes.get(n),trim=raw.trim();if(trim&&STATIC[trim])n.nodeValue=raw.replace(trim,trStatic(trim,l))}
 root.querySelectorAll?.('[placeholder]').forEach(el=>{if(!originalAttrs.has(el))originalAttrs.set(el,el.getAttribute('placeholder'));let src=originalAttrs.get(el);if(STATIC[src])el.setAttribute('placeholder',trStatic(src,l))});
}
function setLanguage(l){if(!LANGS.some(v=>v[0]===l))l='en';localStorage.setItem('plot_ui_language',l);let sel=document.getElementById('languageSelect');if(sel)sel.value=l;apply(document,l)}
function fillSelector(){let s=document.getElementById('languageSelect');if(!s)return;s.innerHTML=LANGS.map(x=>'<option value="'+x[0]+'">'+x[1]+'</option>').join('');s.value=lang()}
function vibes(l=lang()){return VIBES[l]||VIBES.en}
function buildDescription(v,topics,spice,l=lang()){
 let vv=v.slice(0,5).join(', '),tt=topics.slice(0,6).map(x=>topic(x,l)).join(', ');
 const d={
 en:'We are '+(vv||'a close group')+'. We want questions about '+(tt||'friendship, habits and funny situations')+'. Keep the night '+(spice===3?'funny, bold and adult':spice===2?'funny, personal and cheeky':'light, funny and comfortable')+'. Mix laughs and surprises with questions that really test how well we know each other.',
 es:'Somos '+(vv||'un grupo que se conoce bien')+'. Queremos preguntas sobre '+(tt||'amistad, hábitos y situaciones graciosas')+'. Queremos una noche '+(spice===3?'divertida, atrevida y adulta':spice===2?'divertida, personal y un poco picante':'ligera, divertida y cómoda')+'. Mezcla risas y sorpresas con preguntas que prueben cuánto nos conocemos.',
 'pt-BR':'Somos '+(vv||'uma galera que se conhece bem')+'. Queremos perguntas sobre '+(tt||'amizade, hábitos e situações engraçadas')+'. Queremos uma noite '+(spice===3?'divertida, ousada e adulta':spice===2?'divertida, pessoal e atrevida':'leve, divertida e confortável')+'. Misture risadas e surpresas com perguntas que testem o quanto nos conhecemos.',
 fr:'Nous sommes '+(vv||'un groupe qui se connaît bien')+'. Nous voulons des questions sur '+(tt||'l’amitié, les habitudes et les situations drôles')+'. Nous voulons une soirée '+(spice===3?'drôle, audacieuse et adulte':spice===2?'drôle, personnelle et piquante':'légère, drôle et confortable')+'. Mélange rires, surprises et vraies questions pour tester à quel point on se connaît.',
 ja:(vv||'仲の良いグループ')+'です。テーマは'+(tt||'友情、クセ、笑えるシチュエーション')+'。'+(spice===3?'大人向けで攻めた、でも楽しい夜':'自然に笑えて、ちょっと意外な一面が出る夜')+'にしたいです。本当にお互いをどれだけ知っているか試せる質問も混ぜてください。',
 he:'אנחנו '+(vv||'חבורה שמכירה טוב')+'. רוצים שאלות על '+(tt||'חברות, הרגלים וסיטואציות מצחיקות')+'. אנחנו רוצים ערב '+(spice===3?'מצחיק, חצוף ונועז':spice===2?'מצחיק, אישי וקצת חצוף':'קליל, מצחיק ונעים לכולם')+'. תערבב צחוק והפתעה עם שאלות שבאמת בודקות כמה אנחנו מכירים אחד את השני.'
 };return d[l]||d.en
}
window.PT_I18N={LANGS,lang,t,topic,apply,setLanguage,fillSelector,vibes,buildDescription};
})();