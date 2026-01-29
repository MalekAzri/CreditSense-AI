email pour demander de renvoyer un document
remplir les tables par des exemples ( backend )
rendre l'affichage dynamique( nn pas statique )
essayer de lier le dash au module de verif de docs ( affichage resultat dynamique)



remplissez la table au backend avec des données fictives ( utilisez des mails fictives , laissez les vocales vides pour le moment, et utilisez les documents sous docs ( cin et passeport pour le moment )


ajoutez les champs necessaires au vocal ( selon output du module audio)


ajouter au regitsration un champ, banque ( à quel banque il travaille ) et donc il ne verra que les collegues ( qui travauillent à la mm bnaque ( filtrage ))


lorsque je clique sur details d'un mail, je pourrais repondre ( envoie mail auto par le system ) à verifier 



dans scripts il ya un fichier start_bot, nrmlm il reçoit les mails du mail de la banque autoùatiquement ( api ) , je veux que tu fixe l'api localement puisque j'ai pullé je pense qu'elle nexiste pas chez moi maintenant, et que tu execute le pipeline, le module du mail reçoit du mail de la banque directement les mails, il cherche le client en dash , il ajoute le mail au client dans le dash ( via le sender donc ajoutez un champ mail du client au client )  + remplit les champs du mail suite à l'analyse du mail ( intention, ton etc ), les champs doivent etre: subject, sender, status, extracted data , intent, confidence, tone ( urgency, stress, seriousness) voiçi un exemplaire de resultat du module:==================================================
TEST RESULT (REAL-TIME)
==================================================
Subject   : Credit
Sender    : Youssef Turki <youssefturki999@gmail.com>
Status    : processed

EXTRACTED DATA (PHASE 1 & 2):
  Clean Text: Credit....
  Credit Type: None
  Amount: None None
  Client Name: None
  Phone: None
  CIN: None
  Reference: None

AI ANALYSIS:
  Intent     : CREDIT_REQUEST
  Confidence : 1.0
  Tone       : Urgency=0.48, Stress=0.26, Seriousness=0.86
==================================================,
