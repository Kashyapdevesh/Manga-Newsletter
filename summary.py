from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6") #1.14GB

ARTICLE = """ Death Note Manga is a Japanese manga series written by Tsugumi Ohba and illustrated by Takeshi Obata. The storyline follows a high school student who falls upon a supernatural laptop from a shinigami named Ryuk that allows its user the power to kill anyone whose name and face he understands, Light Yagami. The series centres around Light's subsequent attempts to make and rule a world "cleansed of evil" as a "God" using this located laptop, as well as the efforts of a detective called L to stop him. Light Yagami is a blase young prodigy who resents all things bad. His life experiences a radical change when he falls upon the "Death Note", a laptop that kills anyone whose name is written inside. After testing with all the laptop, its credibility is confirmed by Light and is joined through an unexpected house guest - the previous owner of the laptop, a shinigami called Ryuk. Light tells Ryuk of his plan to exterminate all of the individuals he considers unfair and wrong in the planet, until only individuals whom he's deemed truthful and type stay. Once he ends creating this utopia, he means to rule over it as the self proclaimed "God of the new world".


Main character in Death Note manga

Shortly, the inexplicable deaths of offenders get the eye of Interpol as well as the world-renowned detective, "L". L stages a fake public appearance and immediately deduces the serial killer, openly called "Kira" (based on the Japanese pronunciation of the word "killer"), is situated in the Kanto area and will kill people without direct contact. Lighting starts a cat and mouse game with him, and recognizes that L will be his biggest hindrance, in the efforts of stopping his life and learning his identity.

By helping his task force and L track down Kira light efforts to produce an alibi. His strategy is impeded well-known model Misa Amane by a lovestruck second Kira, and her shinigami Rem. Misa trails him to his house, where he consents to be her boyfriend in exchange for her obedience and conformity and identifies Light as the primary Kira. Nevertheless, Misa's infatuation with Light shortly drives her to make several errors that are tactical and L begins to discover the two increasingly more funny from the second. Misa interrogated and is soon arrested and Light turns himself in voluntarily shortly after. They both subsequently relinquish ownership of the Death Notes, erasing their memories of everything they did involved using the publication.


Death Note Manga

Throughout their detention, a third Kira appears. L releases them plus they can be put under house arrest in the headquarters of L when it becomes clear that Misa and Light cannot be carrying out the homicides of the third Kira. The task force get him and identify the third Kira as Yotsuba Group executive Kyosuke Higuchi. Upon touching the laptop, Light recovers his memories as Kira and kills Higuchi, recovering possession of the Death Note "exactly as planned". The task force verify the existence of shinigami and learns of the Death Notes. His elaborate strategy is subsequently completed by light into killing his guard Watari and L to save Misa's life by manipulating Rem. Rem expires herself because killing to prolong the lifespan of individual breaks shinigami law. Upon L's departure, Light becomes the second "L" and continues his charade of hunting for Kira while carrying out the crimes himself.

The story picks up four years after, with Kira pulling a swell of public support as well as a sizable network of contacts. Two young men, raised to L as possible successors, are shown - Near, a detective and the United States Government associated, and Mello, an associate of the Mafia. As his first action against Kira, Mello efforts to obtain the Death Note held by the Kira task force, by kidnapping the manager of the National Police Agency in Japan. When Light homicides the manager out of hand this strategy is stymied. Refocusing on the families of the task force, Mello kidnaps the sister Sayu as a replacement of Light; the task force's laptop is lost to Mello, although she's immediately saved. To recover it, Light's dad Soichiro commerces half of his remaining life to Ryuk for the "Shinigami Eyes" - the skill to view people's names on sight. During an assault on the headquarters of Mello, Soichiro learns the name of Mello, but doesn't kill him. He's shot at repeatedly a strike, and dies soon later in hospital.





After this, several and Near members of the task force start to imagine of being Kira Light. In result, Light gets Misa to quit her laptop and lifts another "Kira", Teru Mikami, a prosecutor and fervent supporter of Kira. Mikami kills Kira's former spokesman for being selfish and recruits the former girlfriend of Light, a newscaster and Kiyomi Takada, to replace him. Light shows himself to Takada as the first Kira, and understanding that the other Kiras and he are under Near's surveil, builds a decoy strategy to hide the location of the authentic Death Note.

Mello kidnaps and returns Takada, who kills him with a laptop piece that is concealed. Light subsequently gets Takada commit suicide from implicating him to keep her, but Mikami, oblivious of the activities of Light, tries to kill her as well. This exposes the true Death Note Mikami has hidden, showing the strategy of Light in the final minute. In the story's climax, the two investigation teams meet in the "Yellow Box Warehouse". Mikami, who writes down the names of everybody in the warehouse except Light soon joins them. Near subsequently shows that he replaced the laptop of Mikami using a forgery and the names written implicate Light as Kira. In despair, Light attempts to make use of the laptop bit that is final in his watch to kill Near, but task force member Touta Matsuda, who's enraged in the way in which Light called his own daddy a victim, shoots him several times. Ryuk realises Light uses his private Death Note to kill Light having a heart attack, as he promised to do at the start of the narrative and has lost.

Other manga:
+ Terra Formars
+ Claymore manga
  
"""
print(summarizer(ARTICLE, truncation=True))

