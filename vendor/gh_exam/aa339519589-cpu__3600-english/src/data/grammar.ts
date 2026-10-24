import type { GrammarLesson, Level } from '../types'

type ExampleSeed = [sentence: string, note: string, focus: string]
type TopicSeed = {
  title: string
  summary: string
  examples: ExampleSeed[]
  choice: [correct: string, contrast: string]
  rule: string
  transfer: [correct: string, contrast: string]
}

export const grammarStages: Array<{ id: number; label: string; title: string; level: Level }> = [
  { id: 1, label: '第一阶段', title: '句子起点', level: 'basic' },
  { id: 2, label: '第二阶段', title: '时间与提问', level: 'basic' },
  { id: 3, label: '第三阶段', title: '描述与比较', level: 'middle' },
  { id: 4, label: '第四阶段', title: '动作的关系', level: 'middle' },
  { id: 5, label: '第五阶段', title: '从句与连接', level: 'advanced' },
  { id: 6, label: '第六阶段', title: '复杂表达', level: 'advanced' },
]

const stageTopics: TopicSeed[][] = [
  [
    {
      title: '句子的骨架', summary: '先找到谁，再找到发生了什么。',
      examples: [['I read every night.', '我每晚阅读。', 'I + read'], ['The bell rang.', '铃响了。', 'bell + rang'], ['Mina smiled.', 'Mina 笑了。', 'Mina + smiled']],
      choice: ['Mina opens the window.', 'Mina the window opens.'],
      rule: '英语陈述句通常先放主语，再放谓语。其他时间、地点和对象都围绕这条主干展开。',
      transfer: ['The old clock stopped.', 'The old clock stopping.'],
    },
    {
      title: 'be 连接状态', summary: '身份、状态和位置需要一座桥。',
      examples: [['She is quiet.', '她很安静。', 'is + quiet'], ['They are students.', '他们是学生。', 'are + students'], ['The keys are here.', '钥匙在这里。', 'are + here']],
      choice: ['The room is warm.', 'The room warm.'],
      rule: '当句子表达“是什么、怎么样、在哪里”时，be 动词把主语和后面的信息连接起来。',
      transfer: ['I am ready.', 'I ready.'],
    },
    {
      title: '人称代词', summary: '不重复名字，仍然知道是谁。',
      examples: [['Lina is here. She is early.', 'Lina 到了。她来得早。', 'Lina → she'], ['Tom and I read. We take notes.', 'Tom 和我阅读。我们做笔记。', 'Tom and I → we'], ['I saw Ben. I waved to him.', '我看见 Ben，向他挥手。', 'Ben → him']],
      choice: ['Maya called me.', 'Maya called I.'],
      rule: '主语位置用 I/he/she/we/they；动词或介词后用 me/him/her/us/them。',
      transfer: ['They invited us.', 'Them invited we.'],
    },
    {
      title: '一个还是多个', summary: '名词会把数量写在自己身上。',
      examples: [['one book', '一本书', 'book'], ['two books', '两本书', 'books'], ['three boxes', '三个盒子', 'boxes']],
      choice: ['There are two lamps.', 'There are two lamp.'],
      rule: '可数名词表示多个时通常加 -s 或 -es；不规则复数需要单独记住，如 children、men。',
      transfer: ['She bought three brushes.', 'She bought three brush.'],
    },
    {
      title: 'a、an 与 the', summary: '第一次出现，还是双方都知道。',
      examples: [['I saw a bird.', '我看见一只鸟，第一次提到。', 'a'], ['She ate an apple.', 'apple 以元音音素开头。', 'an'], ['The bird flew away.', '再次提到那只鸟。', 'the']],
      choice: ['I opened a window. The window was dusty.', 'I opened the window. A window was dusty.'],
      rule: 'a/an 引入一个不特定的人或物；the 指向双方已经知道、再次提到或唯一的对象。',
      transfer: ['He found an old map.', 'He found a old map.'],
    },
    {
      title: 'this、that、these、those', summary: '远近和单复数一起决定指示词。',
      examples: [['This book is mine.', '这本书，近处单数。', 'this'], ['That house is old.', '那座房子，远处单数。', 'that'], ['These keys are new. Those keys are old.', '这些近，那些远，都是复数。', 'these / those']],
      choice: ['Those stars are bright.', 'That stars are bright.'],
      rule: 'this/these 指近处，that/those 指远处；this/that 配单数，these/those 配复数。',
      transfer: ['This chair is comfortable.', 'These chair is comfortable.'],
    },
    {
      title: '谁的东西', summary: '所有关系放在名词前。',
      examples: [['my notebook', '我的笔记本', 'my'], ['Lina’s coat', 'Lina 的外套', 'Lina’s'], ['their room', '他们的房间', 'their']],
      choice: ['This is Noah’s bicycle.', 'This is Noah bicycle.'],
      rule: '形容词性物主代词 my/your/his/her/our/their 放在名词前；名词所有格通常加 ’s。',
      transfer: ['Our teacher knows her name.', 'Ours teacher knows she name.'],
    },
    {
      title: 'there be', summary: '先让某物出现在场景里。',
      examples: [['There is a note on the desk.', '桌上有一张纸条。', 'There is'], ['There are two chairs by the wall.', '墙边有两把椅子。', 'There are'], ['There was a light upstairs.', '楼上曾亮着一盏灯。', 'There was']],
      choice: ['There are three windows.', 'There is three windows.'],
      rule: 'there be 用来引出“某处有某物”；be 的单复数通常跟后面最靠近的名词一致。',
      transfer: ['There is some water in the glass.', 'There are some water in the glass.'],
    },
  ],
  [
    {
      title: '一般现在时', summary: '习惯、规律和稳定事实。',
      examples: [['I walk to school.', '我平时步行上学。', 'walk'], ['Water boils at 100°C.', '水在 100°C 沸腾。', 'boils'], ['We read after dinner.', '我们晚饭后阅读。', 'read']],
      choice: ['Birds build nests.', 'Birds are building nests every spring.'],
      rule: '一般现在时描述反复发生的习惯、客观规律和长期状态。',
      transfer: ['The shop closes at nine.', 'The shop is closing at nine every day.'],
    },
    {
      title: '第三人称单数', summary: 'he、she、it 让动词多一个尾音。',
      examples: [['She reads quietly.', '她安静地阅读。', 'reads'], ['Tom watches the road.', 'Tom 看着路。', 'watches'], ['It carries water.', '它运水。', 'carries']],
      choice: ['Mira studies at night.', 'Mira study at night.'],
      rule: '一般现在时里，主语是 he/she/it 或单数名词时，实义动词通常加 -s/-es。',
      transfer: ['The bus arrives at six.', 'The bus arrive at six.'],
    },
    {
      title: '现在进行时', summary: '把镜头停在此刻。',
      examples: [['It is raining.', '此刻正在下雨。', 'is raining'], ['They are waiting outside.', '他们正在外面等。', 'are waiting'], ['I am writing now.', '我现在正在写。', 'am writing']],
      choice: ['The baby is sleeping now.', 'The baby sleeps now.'],
      rule: 'be + doing 表示正在进行或当前阶段持续的动作。',
      transfer: ['We are looking for the key.', 'We looking for the key.'],
    },
    {
      title: '一般过去时', summary: '把动作放进已经结束的时间。',
      examples: [['I called her yesterday.', '我昨天给她打了电话。', 'called'], ['The rain stopped.', '雨停了。', 'stopped'], ['She went home early.', '她早早回家了。', 'went']],
      choice: ['We visited the museum last week.', 'We visit the museum last week.'],
      rule: '一般过去时描述已经结束的过去动作；规则动词加 -ed，不规则动词需要变化。',
      transfer: ['He found the letter this morning.', 'He finds the letter this morning.'],
    },
    {
      title: '将来：will 与 going to', summary: '临时决定，还是已有打算。',
      examples: [['I’ll answer the door.', '听见门铃后临时决定。', 'will'], ['We are going to move.', '已经有搬家的计划。', 'going to'], ['It is going to rain.', '有迹象表明要下雨。', 'going to']],
      choice: ['Look at those clouds. It is going to rain.', 'Look at those clouds. It rains.'],
      rule: 'will 常用于即时决定和预测；be going to 常表示已有计划或眼前有迹象的将来。',
      transfer: ['I think you will enjoy the book.', 'I think you enjoy the book tomorrow.'],
    },
    {
      title: '动作句的否定', summary: 'do、does、did 来承担 not。',
      examples: [['I do not know.', '我不知道。', 'do not'], ['She does not drive.', '她不开车。', 'does not'], ['They did not leave.', '他们没有离开。', 'did not']],
      choice: ['He does not like coffee.', 'He not likes coffee.'],
      rule: '一般时态的实义动词句用 do/does/did + not；后面的动词回到原形。',
      transfer: ['We did not see the sign.', 'We did not saw the sign.'],
    },
    {
      title: '一般疑问句', summary: '把帮助动词提到前面。',
      examples: [['Do you read here?', '你在这里读书吗？', 'Do'], ['Does she know?', '她知道吗？', 'Does'], ['Did they call?', '他们打电话了吗？', 'Did']],
      choice: ['Does Arun work here?', 'Is Arun work here?'],
      rule: '一般时态的动作句用 Do/Does/Did 开头；be 动词句直接把 be 提到主语前。',
      transfer: ['Are the keys inside?', 'Do the keys inside?'],
    },
    {
      title: '特殊疑问句', summary: '先问缺少的信息，再保持疑问语序。',
      examples: [['Where do you live?', '你住在哪里？', 'Where + do'], ['Why did she leave?', '她为什么离开？', 'Why + did'], ['Who called you?', '谁给你打电话了？', 'Who']],
      choice: ['When does the train leave?', 'When the train leaves?'],
      rule: '疑问词后通常接一般疑问句语序；当 who/what 本身作主语时，不再加 do。',
      transfer: ['What happened outside?', 'What did happen outside?'],
    },
  ],
  [
    {
      title: '形容词与副词', summary: '一个修饰名词，一个修饰动作。',
      examples: [['a quiet room', '安静的房间', 'quiet'], ['She spoke quietly.', '她轻声说。', 'quietly'], ['The soup tastes good.', '汤尝起来不错。', 'good']],
      choice: ['He answered politely.', 'He answered polite.'],
      rule: '形容词修饰名词或跟在系动词后；副词常修饰动作、形容词或整句。',
      transfer: ['The music sounds beautiful.', 'The music sounds beautifully.'],
    },
    {
      title: '频率的位置', summary: 'always、often、never 放在合适的位置。',
      examples: [['I often walk home.', '我经常走回家。', 'often + walk'], ['She is always early.', '她总是很早。', 'is + always'], ['They never complain.', '他们从不抱怨。', 'never + complain']],
      choice: ['He usually reads before bed.', 'He reads usually before bed.'],
      rule: '频率副词通常放在实义动词前、be 动词后；sometimes 的位置更灵活。',
      transfer: ['Mina is rarely late.', 'Mina rarely is late.'],
    },
    {
      title: '可数与不可数', summary: '有些名词能逐个数，有些不能。',
      examples: [['three ideas', '三个想法，可数。', 'ideas'], ['some advice', '一些建议，不可数。', 'advice'], ['a piece of information', '一条信息。', 'a piece of']],
      choice: ['She gave me some advice.', 'She gave me an advice.'],
      rule: '不可数名词通常没有复数，也不直接与 a/an 连用；需要数量时用 piece、cup 等单位。',
      transfer: ['We need more information.', 'We need more informations.'],
    },
    {
      title: 'some、any、much、many', summary: '数量词跟着句型和名词类型走。',
      examples: [['I have some questions.', '肯定句中的一些问题。', 'some'], ['Do you have any water?', '疑问句中的水。', 'any'], ['How many books?', '多少本书，可数。', 'many']],
      choice: ['There is not much time.', 'There are not many time.'],
      rule: 'many 修饰可数复数，much 修饰不可数；some 常见于肯定句，any 常见于疑问和否定。',
      transfer: ['We do not have any chairs.', 'We do not have some chairs.'],
    },
    {
      title: '比较级', summary: '两者之间看出差异。',
      examples: [['This road is longer.', '这条路更长。', 'longer'], ['Mira reads more slowly.', 'Mira 读得更慢。', 'more slowly'], ['The blue one is better.', '蓝色的更好。', 'better']],
      choice: ['Today is colder than yesterday.', 'Today is more cold than yesterday.'],
      rule: '短形容词常加 -er，较长词用 more；比较对象常由 than 引出。',
      transfer: ['This question is more difficult.', 'This question is difficulter.'],
    },
    {
      title: '最高级', summary: '在一个范围里找到最突出者。',
      examples: [['the tallest tree', '最高的树。', 'the tallest'], ['the most useful tool', '最有用的工具。', 'the most useful'], ['her best poem', '她最好的诗。', 'best']],
      choice: ['It is the oldest house in town.', 'It is oldest house in town.'],
      rule: '最高级前通常有 the，并配合 in/of 表示比较范围；不规则形式要单独记。',
      transfer: ['This was the most surprising part.', 'This was the surprisingest part.'],
    },
    {
      title: '时间与地点介词', summary: '点、面、范围各有位置。',
      examples: [['at six', '在六点，一个时间点。', 'at'], ['on Monday', '在星期一。', 'on'], ['in July', '在七月，一个时间范围。', 'in']],
      choice: ['The keys are on the table.', 'The keys are in the table.'],
      rule: 'at 常指点，on 常指表面或具体日期，in 常指较大空间与时间范围。',
      transfer: ['We arrived in Chicago at noon.', 'We arrived at Chicago in noon.'],
    },
    {
      title: 'and、but、or、so', summary: '让两个意思并列、转折、选择或承接。',
      examples: [['She opened the book and began to read.', '动作并列。', 'and'], ['It was late, but we stayed.', '意思转折。', 'but'], ['It rained, so we went inside.', '结果承接。', 'so']],
      choice: ['I was tired, but I finished the work.', 'I was tired, so I did not finish but.'],
      rule: 'and 并列，but 转折，or 选择，so 引出结果。先判断两个分句的逻辑关系。',
      transfer: ['Hurry, or you will miss the bus.', 'Hurry, and you will miss the bus.'],
    },
  ],
  [
    {
      title: '情态动词的力度', summary: 'can、should、must、may 不是同一种语气。',
      examples: [['You can leave now.', '可以离开。', 'can'], ['You should rest.', '建议休息。', 'should'], ['You must stop.', '必须停止。', 'must']],
      choice: ['It may rain tonight.', 'It must rain tonight, but I am not sure.'],
      rule: '情态动词表达能力、许可、建议、义务或推测；后面接动词原形。',
      transfer: ['You should check the address.', 'You should to check the address.'],
    },
    {
      title: '被动语态', summary: '把目光放在动作的承受者上。',
      examples: [['The bridge was built in 1890.', '桥是文章主角。', 'was built'], ['English is spoken here.', '这里说英语。', 'is spoken'], ['The door has been locked.', '门已经被锁。', 'has been locked']],
      choice: ['The letter was written by hand.', 'The letter wrote by hand.'],
      rule: '被动语态由 be + 过去分词构成；时态变化落在 be 上。',
      transfer: ['The rooms are cleaned every day.', 'The rooms clean every day.'],
    },
    {
      title: '现在完成时', summary: '过去发生，影响仍在现在。',
      examples: [["I've lost my key.", '钥匙现在仍不见。', 'have lost'], ['She has finished the book.', '书现在已经读完。', 'has finished'], ['We have lived here for years.', '居住延续到现在。', 'have lived']],
      choice: ["I've broken my glasses.", 'I broke my glasses in 2020.'],
      rule: 'have/has + 过去分词把过去与现在连接起来，可表达结果、经历或持续。',
      transfer: ['He has just arrived.', 'He just arrive.'],
    },
    {
      title: '完成时还是过去时', summary: '看时间是否结束，看结果是否仍相关。',
      examples: [['I saw her yesterday.', 'yesterday 已结束。', 'saw'], ["I've seen that film.", '表达经历，不说具体时间。', 'have seen'], ['She lived there in 2019.', '2019 已结束。', 'lived']],
      choice: ['We visited Paris last year.', "We've visited Paris last year."],
      rule: '明确、结束的过去时间用一般过去时；不强调具体时间、与现在相关时用现在完成时。',
      transfer: ["I haven't finished yet.", 'I did not finish yet yesterday.'],
    },
    {
      title: '动名词', summary: '把动作当成一件事来谈。',
      examples: [['Reading helps me think.', '阅读这件事帮助思考。', 'Reading'], ['She enjoys walking.', 'enjoy 后接 doing。', 'walking'], ['He left without saying goodbye.', '介词后接 doing。', 'saying']],
      choice: ['They avoid driving at night.', 'They avoid to drive at night.'],
      rule: '动名词 doing 可以作主语、宾语或介词宾语；部分动词固定接 doing。',
      transfer: ['Swimming is good exercise.', 'Swim is good exercise.'],
    },
    {
      title: '不定式', summary: '把动作指向目的、计划或将来。',
      examples: [['I want to leave.', '想要离开。', 'to leave'], ['She came to help.', '来是为了帮助。', 'to help'], ['It is hard to explain.', '解释很难。', 'to explain']],
      choice: ['We decided to wait.', 'We decided waiting.'],
      rule: 'to + 动词原形常表达目的，也跟在 want、decide、hope 等动词后。',
      transfer: ['He opened the door to let us in.', 'He opened the door letting us in purpose.'],
    },
    {
      title: 'that 宾语从句', summary: '把一整句话放在 think、know、say 后面。',
      examples: [['I think that she is right.', '我认为她是对的。', 'that'], ['We know that the shop is closed.', '我们知道店关了。', 'that'], ['He said that he was tired.', '他说他累了。', 'that']],
      choice: ['She believes that the plan will work.', 'She believes that will the plan work.'],
      rule: 'that 引导的宾语从句使用陈述语序；口语中 that 常可省略，但句子结构不变。',
      transfer: ['I noticed that the light was on.', 'I noticed that was the light on.'],
    },
    {
      title: 'who、which、that 定语从句', summary: '紧跟名词，回答“哪一个”。',
      examples: [['The girl who lives upstairs sings.', 'who 指人。', 'who'], ['The book which is missing is mine.', 'which 指物。', 'which'], ['The train that stops here is late.', 'that 可指人或物。', 'that']],
      choice: ['The coat that I bought is warm.', 'The coat is warm that I bought.'],
      rule: '定语从句紧跟被说明的名词；who 指人，which 指物，that 在限制性从句中常都可用。',
      transfer: ['The teacher who helped me has left.', 'The teacher which helped me has left.'],
    },
  ],
  [
    {
      title: '关系代词的省略', summary: '当关系词不作主语时，可以轻轻拿掉。',
      examples: [['The book (that) I bought is here.', 'that 作 bought 的宾语，可省略。', '(that)'], ['The person (who) we met called.', 'who 作 met 的宾语，可省略。', '(who)'], ['The girl who called is Lina.', 'who 作 called 的主语，不能省略。', 'who']],
      choice: ['The film we watched was quiet.', 'The film watched was quiet.'],
      rule: '关系代词在从句中作宾语时可省略；作主语时必须保留。',
      transfer: ['The letter that arrived today is yours.', 'The letter arrived today is yours.'],
    },
    {
      title: 'when 与 while', summary: '一个时间点，或一段同时进行的背景。',
      examples: [['When the bell rang, we left.', '铃响这个时间点。', 'when'], ['While I was reading, she cooked.', '两个动作同时延续。', 'while'], ['Call me when you arrive.', '到达时给我电话。', 'when']],
      choice: ['While it was raining, we stayed inside.', 'While it rained once, we stayed inside.'],
      rule: 'when 可接时间点或时间段；while 更强调两个持续动作同时发生。',
      transfer: ['I smiled when I saw her.', 'I smiled while I saw her once.'],
    },
    {
      title: 'because 与 although', summary: '一个给原因，一个承认阻力。',
      examples: [['We stayed because it was raining.', '给出原因。', 'because'], ['Although it was late, we stayed.', '承认转折背景。', 'although'], ['She left because she was tired.', '因为累而离开。', 'because']],
      choice: ['Although he was nervous, he spoke clearly.', 'Although he was nervous, but he spoke clearly.'],
      rule: 'because 引原因；although 引让步。although 与 but 通常不在同一句中重复使用。',
      transfer: ['We turned back because the road was closed.', 'We turned back although the road was closed, so.'],
    },
    {
      title: '真实条件句', summary: '条件可能发生，结果也可能发生。',
      examples: [['If it rains, we will stay home.', '可能下雨，可能留在家。', 'if + present'], ['If you heat ice, it melts.', '普遍规律。', 'if'], ['I will call if I am late.', '如果迟到就打电话。', 'if']],
      choice: ['If she comes, I will tell her.', 'If she will come, I tell her.'],
      rule: '真实将来条件句中，if 从句常用一般现在时，主句用 will；不要在 if 从句重复 will。',
      transfer: ['If you press this button, the light turns on.', 'If you will press this button, the light turns on.'],
    },
    {
      title: '间接引语', summary: '转述别人说过的话。',
      examples: [["She said, ‘I am tired.’", '原话。', 'am'], ['She said that she was tired.', '过去转述，时态后移。', 'was'], ['He told me that he would call.', 'will 后移为 would。', 'would']],
      choice: ['Mina said that she had lost the key.', 'Mina said that I have lost the key.'],
      rule: '过去时的转述动词常带来人称、时间和时态的相应变化；信息仍为事实时可不机械后移。',
      transfer: ['He told us that the train was late.', 'He said us that the train is late.'],
    },
    {
      title: '分词压缩', summary: '共享主语时，把重复折叠起来。',
      examples: [['Walking home, she found a coin.', 'she 主动走路。', 'Walking'], ['Surprised by the news, he paused.', 'he 被消息惊到。', 'Surprised'], ['Built in 1890, the bridge is still used.', '桥被建造。', 'Built']],
      choice: ['Looking through the window, I saw the sea.', 'Looked through the window, I saw the sea.'],
      rule: '现在分词常表示主动或进行，过去分词常表示被动或完成；隐藏主语必须与主句一致。',
      transfer: ['Delayed by snow, the train arrived late.', 'Delaying by snow, the train arrived late.'],
    },
    {
      title: '使役结构', summary: '让、请、使别人完成动作。',
      examples: [['She made me wait.', 'make + 人 + 动词原形。', 'made me wait'], ['I had my bike repaired.', '请人修车。', 'had + repaired'], ['He let us leave.', 'let + 人 + 动词原形。', 'let us leave']],
      choice: ['The joke made everyone laugh.', 'The joke made everyone to laugh.'],
      rule: 'make/let 后常接人 + 动词原形；have/get something done 表示让某事被完成。',
      transfer: ['I got the window fixed.', 'I got the window fix.'],
    },
    {
      title: '主谓一致', summary: '真正的主语决定动词单复数。',
      examples: [['The list is long.', '主语是单数 list。', 'is'], ['The books on the desk are mine.', '主语是复数 books。', 'are'], ['Either answer is possible.', 'either 作单数。', 'is']],
      choice: ['The box of letters is heavy.', 'The box of letters are heavy.'],
      rule: '不要被主语后的介词短语干扰；动词与真正的中心主语保持一致。',
      transfer: ['Each of the rooms has a window.', 'Each of the rooms have a window.'],
    },
  ],
  [
    {
      title: '过去完成时', summary: '站在过去，再往前看一步。',
      examples: [['The train had left before we arrived.', '到达前，车已经走了。', 'had left'], ['She had never seen snow.', '到那个过去时点前从未见过。', 'had seen'], ['After he had called, he waited.', '先打电话，后等待。', 'had called']],
      choice: ['By noon, they had finished the work.', 'By noon, they finished already before.'],
      rule: 'had + 过去分词表示“过去的过去”，用来理清两个过去动作的先后。',
      transfer: ['I realized that I had left my bag behind.', 'I realized that I leave my bag behind.'],
    },
    {
      title: '将来完成时', summary: '从未来回望已经完成的动作。',
      examples: [['By Friday, I will have finished.', '到周五时会已经完成。', 'will have finished'], ['She will have left by then.', '到那时她会已经离开。', 'will have left'], ['In June, we will have lived here for a year.', '到六月满一年。', 'will have lived']],
      choice: ['By next week, they will have arrived.', 'By next week, they will arrive already before.'],
      rule: 'will have + 过去分词强调动作在未来某个时间之前完成。',
      transfer: ['By 2030, the city will have changed greatly.', 'By 2030, the city changes greatly already.'],
    },
    {
      title: '虚拟条件句', summary: '动词后退一步，表达与现实的距离。',
      examples: [['If I knew, I would tell you.', '我其实不知道。', 'knew / would'], ['If I had more time, I would stay.', '我现在没有更多时间。', 'had / would'], ['If she had called, I would have come.', '她当时没有打电话。', 'had called']],
      choice: ['If I were you, I would wait.', 'If I am you, I will wait.'],
      rule: '虚拟语气用形式上的过去表达不真实；对过去的遗憾用 had done / would have done。',
      transfer: ['If they had left earlier, they would have caught the train.', 'If they left earlier yesterday, they will catch the train.'],
    },
    {
      title: '倒装强调', summary: '限制词来到句首，语序回应重音。',
      examples: [['Never have I seen such light.', 'never 置于句首。', 'have I'], ['Only then did she understand.', 'only then 置于句首。', 'did she'], ['Not until noon did he arrive.', 'not until 置于句首。', 'did he']],
      choice: ['Rarely do we hear such honesty.', 'Rarely we hear such honesty.'],
      rule: '否定或限制性表达位于句首时，主句常用部分倒装：助动词在主语前。',
      transfer: ['Only after reading it did I understand.', 'Only after reading it I understood.'],
    },
    {
      title: '强调句', summary: '用 It is/was 把重音放在一个成分上。',
      examples: [['It was Lina who found the key.', '强调 Lina。', 'It was Lina'], ['It is today that we begin.', '强调 today。', 'It is today'], ['It was in the library that they met.', '强调地点。', 'in the library']],
      choice: ['It was the final page that changed my mind.', 'It was the final page changed my mind.'],
      rule: 'It is/was + 被强调成分 + that/who + 其余部分；去掉框架后仍应是完整句子。',
      transfer: ['It was yesterday that she called.', 'It yesterday was she called.'],
    },
    {
      title: 'what 与 whether 名词性从句', summary: '让从句在句中承担一个名词位置。',
      examples: [['What she said surprised me.', '她说的内容作主语。', 'What'], ['I wonder whether he knows.', '是否知道作宾语。', 'whether'], ['The question is what we should do.', '作表语。', 'what']],
      choice: ['What matters is how we respond.', 'That matters is how we respond.'],
      rule: 'what 本身在从句中作成分，意为“……的事物”；whether 表示“是否”，从句保持陈述语序。',
      transfer: ['I do not know whether the door is open.', 'I do not know whether is the door open.'],
    },
    {
      title: '同位语从句', summary: '在抽象名词后说明它的具体内容。',
      examples: [['The news that he had returned spread quickly.', 'that 从句说明 news 的内容。', 'news that'], ['We accepted the idea that change takes time.', '说明 idea。', 'idea that'], ['There is evidence that the climate is changing.', '说明 evidence。', 'evidence that']],
      choice: ['The fact that she stayed mattered.', 'The fact which she stayed mattered.'],
      rule: '同位语从句常跟在 fact、news、idea、hope、evidence 后，that 在从句中不作成分。',
      transfer: ['They expressed the hope that peace would return.', 'They expressed the hope which peace would return.'],
    },
    {
      title: '长句的主干', summary: '先找到带时态的主谓，再安放修饰。',
      examples: [['The study conducted in five cities suggests a change.', '主干：study suggests。', 'study suggests'], ['The letters found upstairs reveal the truth.', '主干：letters reveal。', 'letters reveal'], ['What she discovered changed the plan.', '主干：从句作主语 + changed。', 'changed']],
      choice: ['A report published yesterday shows that prices fell.', 'Yesterday prices published a report that shows.'],
      rule: '先找带时态的核心谓语和它的主语；分词、介词短语和从句随后归位。',
      transfer: ['The book that you lent me explains the idea clearly.', 'The book lent me the idea that explains clearly.'],
    },
  ],
]

export const grammarLessons: GrammarLesson[] = stageTopics.flatMap((topics, stageIndex) => {
  const stage = grammarStages[stageIndex]
  return topics.map((topic, topicIndex) => {
    const reverseFirst = topicIndex % 2 === 1
    const reverseTransfer = topicIndex % 2 === 0
    const [correct, contrast] = topic.choice
    const [transferCorrect, transferContrast] = topic.transfer
    return {
      id: `g-stage-${stage.id}-${String(topicIndex + 1).padStart(2, '0')}`,
      number: String(topicIndex + 1).padStart(2, '0'),
      level: stage.level,
      stage: stage.id,
      title: topic.title,
      englishTitle: topic.title,
      duration: 7 + Math.floor(stage.id / 2),
      description: topic.summary,
      examples: topic.examples.map(([sentence, note, focus]) => ({ sentence, note, focus })),
      challenge: {
        scene: topic.summary,
        prompt: '哪一句更自然？',
        options: reverseFirst ? [contrast, correct] : [correct, contrast],
        answer: correct,
        nudge: `回看上面的例句，留意 ${topic.examples[0][2]}。`,
        insight: topic.rule,
        transfer: {
          prompt: '换一个语境，再选一次。',
          options: reverseTransfer ? [transferContrast, transferCorrect] : [transferCorrect, transferContrast],
          answer: transferCorrect,
        },
        takeaway: `你已经完成“${topic.title}”。下一次先认出这种结构。`,
      },
    }
  })
})
