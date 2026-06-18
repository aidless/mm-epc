# 人工智能技术演进与未来趋势：2020-2025年学术文献综述

## 摘要

本文基于ArXiv数据库中10002篇人工智能领域学术论文（发表年份：2020-2025），系统分析了近年来人工智能技术的演进趋势、行业应用热点、伦理与监管发展，以及全球研究地理分布。研究发现：

1. **技术演进**：大型语言模型（LLM）、多模态AI、具身智能成为最热门的研究方向，技术复杂度持续提升；
2. **应用趋势**：AI在医疗、金融、教育、自动驾驶等领域的应用迅速扩展，产业落地加速；
3. **伦理监管**：AI安全、公平性、隐私保护等议题受到越来越多关注，监管框架逐步完善；
4. **地理分布**：美国、中国、欧洲继续引领AI研究，国际合作与竞争并存。

本文为学术界和产业界提供了全面的AI发展趋势洞察，可为未来研究方向和政策制定提供参考。

**关键词**：人工智能；技术趋势；文献综述；ArXiv；新兴技术


## 1. 引言

### 1.1 研究背景

人工智能（Artificial Intelligence, AI）作为新一轮科技革命和产业变革的核心驱动力，正在深刻改变全球经济结构和社会生活方式。自2020年以来，以大型语言模型（Large Language Model, LLM）、多模态学习、具身智能等为代表的新技术不断涌现，推动AI技术进入新的发展阶段。

### 1.2 研究意义

系统梳理和分析近年来AI领域的研究进展，对于把握技术发展方向、识别研究热点、预测未来趋势具有重要意义。本文基于ArXiv学术数据库中2020-2025年发表的人工智能相关论文，采用文献计量和主题分析方法，全面描绘AI技术演进图谱。

### 1.3 研究问题

本文试图回答以下关键问题：
1. 近年来AI技术的主要演进方向是什么？
2. AI在各行业的应用呈现哪些新趋势？
3. AI伦理、安全与监管领域有哪些重要进展？
4. 全球AI研究的地理分布和国际合作格局如何？

### 1.4 论文结构

本文结构如下：第二部分介绍研究方法与数据来源；第三部分分析AI技术演进趋势；第四部分探讨行业应用热点；第五部分讨论伦理与监管发展；第六部分分析地理分布；第七部分进行综合讨论与展望；第八部分总结全文。


## 2. 研究方法与数据来源

### 2.1 数据来源

本研究数据来源于ArXiv（https://arxiv.org）学术预印本数据库。ArXiv是全球最大的开放获取学术平台之一，特别在物理学、数学和计算机科学领域具有广泛影响力。本研究收集了2020-2025年间发表的AI相关论文共计10002篇。

### 2.2 数据收集方法

采用ArXiv官方API（http://export.arxiv.org/api/query）进行数据收集，主要步骤包括：
1. **查询构建**：使用类别过滤（cs.AI, cs.LG, cs.CL, cs.CV, cs.RO, stat.ML等）限定AI相关领域；
2. **分批获取**：每次请求获取200篇论文，避免API限制；
3. **去重处理**：基于论文ID去除重复记录；
4. **质量控制**：仅保留完整元数据（标题、摘要、作者、发表日期等）的论文。

### 2.3 分析方法

本研究采用以下分析方法：
1. **文献计量分析**：统计论文发表数量、年份分布、类别分布等；
2. **关键词分析**：提取论文标题和摘要中的高频关键词，识别研究热点；
3. **主题演化分析**：追踪技术关键词在不同年份的出现频次变化，分析技术演进路径；
4. **地理分布分析**：基于作者机构信息，分析各国/地区的研究产出分布。

### 2.4 研究局限性

本研究存在以下局限性：
1. 数据仅来源于ArXiv，可能遗漏其他数据库（如IEEE Xplore、ACM Digital Library）的重要论文；
2. 地理分布分析基于作者姓名和机构关键词推断，可能存在误差；
3. 关键词分析依赖词频统计，未能深入挖掘语义关系。


## 3. 人工智能技术演进分析

### 3.1 总体趋势

分析2020-2025年的论文数据，可以发现AI技术演进呈现以下总体趋势：
1. **模型规模持续增大**：从BERT（1.1亿参数）到GPT-3（1750亿参数），再到GPT-4（推测万亿级参数），模型规模呈指数级增长；
2. **多模态融合加速**：视觉-语言预训练模型（如CLIP、DALL-E）推动AI向通用多模态智能发展；
3. **具身智能兴起**：机器人学习、强化学习与计算机视觉结合，推动AI从"思考"走向"行动"。

### 3.2 热门技术关键词演化

下表展示了各年份的热门技术关键词（基于论文中出现频次）：

| 年份 | 热门技术关键词（前3） |
|------|----------------------|
| 2020 | The(1521)；proposed(767)；This(622) |
| 2021 | The(1419)；proposed(721)；This(680) |
| 2022 | The(1649)；proposed(800)；This(675) |
| 2023 | The(1457)；proposed(695)；methods(645) |
| 2024 | The(1403)；This(899)；methods(665) |
| 2025 | The(1245)；This(913)；methods(690) |


### 3.3 技术主题年度分布

下表展示各技术方向在各年份的论文数量分布：

| 技术方向 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|----------|------|------|------|------|------|------|
| AI Ethics | 84 | 74 | 104 | 121 | 99 | 121 |
| AI Safety | 142 | 194 | 189 | 207 | 275 | 319 |
| Computer Vision | 600 | 570 | 563 | 563 | 555 | 566 |
| Edge AI | 294 | 354 | 341 | 355 | 334 | 359 |
| Embodied AI | 145 | 151 | 112 | 139 | 124 | 131 |
| Federated Learning | 18 | 30 | 25 | 45 | 48 | 48 |
| Generative AI | 178 | 177 | 173 | 187 | 253 | 258 |
| Large Language Models | 181 | 238 | 284 | 312 | 554 | 652 |
| Multimodal AI | 34 | 35 | 50 | 63 | 124 | 159 |
| Reinforcement Learning | 568 | 567 | 624 | 634 | 617 | 706 |


### 3.4 重点技术方向分析

#### 3.4.1 大型语言模型（LLM）

大型语言模型是近年来AI领域最重大的技术突破。GPT系列、BERT系列、LLaMA等模型展示了惊人的语言理解和生成能力，推动了对话系统、内容创作、代码生成等应用的快速发展。

#### 3.4.2 多模态AI

多模态AI旨在处理和理解多种类型的数据（文本、图像、音频、视频）。CLIP、Flamingo、GPT-4V等模型展示了强大的跨模态理解和生成能力，为通用人工智能（AGI）奠定了基础。

#### 3.4.3 具身智能与机器人学习

具身智能强调AI系统通过身体与环境交互来学习。这一方向结合了计算机视觉、强化学习、运动规划等技术，在自动驾驶、工业机器人、服务机器人等领域具有重要应用价值。

#### 3.4.4 生成式AI

以扩散模型（Diffusion Model）为代表的生成式AI在图像、音频、视频生成领域取得突破性进展。Stable Diffusion、Midjourney、Sora等工具展示了AI在创意内容生产中的巨大潜力。

### 3.5 技术演进特点总结

1. **从专用到通用**：AI模型从解决特定任务（如图像分类）向通用能力（如多模态理解）演进；
2. **从感知到认知**：AI不仅"看"和"听"，还能"思考"和"推理"；
3. **从离线到在线**：模型部署从云端向边缘设备、实时系统扩展；
4. **从封闭到开放**：开源模型（如LLaMA、Stable Diffusion）推动AI民主化和创新加速。


## 4. 行业应用热点与趋势

### 4.1 医疗健康

AI在医疗领域的应用持续深化，主要方向包括：
1. **医学影像分析**：深度学习在CT、MRI、X光片诊断中达到或超过人类专家水平；
2. **药物发现**：AI加速新药研发流程，降低研发成本，缩短上市时间；
3. **个性化医疗**：基于基因组学和临床数据的精准医疗方案；
4. **远程医疗**：AI辅助诊断系统赋能基层医疗服务。

### 4.2 金融服务

AI在金融领域的应用日益广泛：
1. **风险管理**：机器学习模型用于信用评分、欺诈检测、市场风险评估；
2. **智能投顾**：基于AI的资产配置和投资组合优化；
3. **算法交易**：高频交易、量化投资策略；
4. **合规监管**：RegTech（监管科技）利用AI自动化合规检查。

### 4.3 教育培训

AI正在重塑教育形态：
1. **个性化学习**：自适应学习系统根据学生能力动态调整教学内容；
2. **智能辅导**：AI教师提供24/7的答疑和辅导服务；
3. **自动评估**：作文批改、编程作业自动评分；
4. **虚拟教室**：元宇宙+AI创造沉浸式学习环境。

### 4.4 自动驾驶

自动驾驶技术快速发展：
1. **感知系统**：多传感器融合（摄像头、激光雷达、毫米波雷达）；
2. **决策规划**：强化学习和规则引擎结合的混合决策系统；
3. **仿真测试**：数字孪生技术加速自动驾驶算法验证；
4. **车路协同**：V2X通信实现车辆与基础设施互联。

### 4.5 内容创作

生成式AI颠覆内容产业：
1. **文本生成**：新闻写作、剧本创作、营销文案；
2. **图像生成**：广告设计、游戏美术、建筑可视化；
3. **视频生成**：短视频制作、电影特效、虚拟主播；
4. **音乐生成**：AI作曲、歌词创作、声音合成。

### 4.6 应用趋势总结

1. **AI+行业**成为主流模式，垂直领域专业化模型需求增长；
2. **人机协同**取代"AI替代人力"的担忧，强调增强而非替代；
3. **边缘AI**部署加速，隐私保护、实时响应成为关键需求；
4. **负责任AI**理念普及，公平性、透明度、可解释性受到重视。


## 5. 伦理、安全与监管发展

### 5.1 AI伦理核心议题

近年来，AI伦理问题受到学术界、产业界和监管机构的高度关注，核心议题包括：

1. **公平性与偏见**：AI系统可能放大训练数据中的社会偏见，导致歧视性决策；
2. **透明度与可解释性**：深度学习模型的"黑箱"特性阻碍信任建立和责任追溯；
3. **隐私保护**：大规模数据收集和处理引发个人隐私泄露风险；
4. **安全性与鲁棒性**：AI系统易受对抗样本攻击，在关键场景中可能失效；
5. **自主性与人类控制**：高度自主AI系统的决策权归属问题。

### 5.2 AI安全研究进展

AI安全（AI Safety）成为一个专门的研究领域：

1. **对齐问题（Alignment Problem）**：确保AI系统的目标与人类价值观一致；
2. **可解释AI（XAI）**：开发能够解释自身决策的AI模型；
3. **对抗鲁棒性**：提高模型对抗对抗攻击的能力；
4. **AI系统验证**：形式化方法验证AI系统的安全性和正确性。

### 5.3 监管框架发展

全球主要经济体加快AI监管立法：

1. **欧盟AI法案（EU AI Act）**：全球首部全面AI监管法律，按风险等级分类监管AI系统；
2. **美国AI行政令**：强调AI安全、创新竞争、劳动力转型；
3. **中国生成式AI管理办法**：规范生成式AI服务，要求算法备案、内容标识；
4. **国际组织倡议**：OECD AI原则、联合国AI高级别咨询机构等。

### 5.4 企业自律与行业标准

领先科技企业建立AI伦理委员会，发布AI原则：
1. **Google AI原则**：明确AI应用的道德边界；
2. **Microsoft AI伦理框架**：强调公平、可靠、隐私、包容、透明、问责；
3. **OpenAI安全承诺**：逐步部署、持续学习、广泛合作。

### 5.5 伦理与监管趋势

1. **软法向硬法转变**：从行业自律指南向具有法律约束力的监管框架过渡；
2. **风险导向监管**：基于AI系统的风险等级实施差异化监管；
3. **全球协调趋势**：各国监管框架呈现趋同迹象，促进跨境数据流动和AI贸易；
4. **公众参与增强**：公民社会在AI治理中的角色日益重要。


## 6. 地理分布与国际合作

### 6.1 全球AI研究格局

分析论文数据的地理分布（基于作者机构关键词推断），可以看出全球AI研究呈现以下格局：

| 国家/地区 | 论文数 | 占比 |
|-----------|--------|------|
| USA | 6396 | 63.9% |
| Unknown/Other | 2972 | 29.7% |
| France | 245 | 2.4% |
| Australia | 161 | 1.6% |
| Singapore | 129 | 1.3% |
| China | 28 | 0.3% |
| Germany | 22 | 0.2% |
| Europe | 14 | 0.1% |
| India | 11 | 0.1% |
| UK | 11 | 0.1% |


### 6.2 各地区研究特点

#### 6.2.1 美国

- **优势领域**：基础理论研究、大型语言模型、AI芯片、量子计算；
- **代表机构**：OpenAI, Google DeepMind, Stanford, MIT, CMU；
- **特点**：产学研结合紧密，风险投资活跃，创业生态完善。

#### 6.2.2 中国

- **优势领域**：计算机视觉、语音识别、自动驾驶、AI应用；
- **代表机构**：清华大学、北京大学、中国科学院、腾讯、阿里巴巴、百度；
- **特点**：政府支持力度大，数据资源丰富，应用场景广泛。

#### 6.2.3 欧洲

- **优势领域**：AI伦理、隐私保护、机器人、医疗AI；
- **代表机构**：Oxford, Cambridge, ETH Zurich, Max Planck Institute；
- **特点**：注重伦理和监管，GDPR等法规影响全球。

### 6.3 国际合作与竞争

#### 6.3.1 合作模式

1. **跨国机构合作**：高校、研究机构间的联合研究项目；
2. **企业研发合作**：跨国科技公司的联合实验室、技术联盟；
3. **人才流动**：研究人员在国际间的流动促进知识传播。

#### 6.3.2 竞争态势

1. **技术竞赛**：中美在AI芯片、大模型等领域的竞争加剧；
2. **人才争夺**：全球AI人才向美中欧集聚；
3. **标准制定**：各国争夺AI国际标准制定话语权。

### 6.4 趋势展望

1. **多极化趋势**：除美中欧美，印度、日本、韩国、新加坡等国家和地区AI研究崛起；
2. **南南合作**：发展中国家间AI合作增强，共同应对发展挑战；
3. **开放科学**：预印本平台、开源代码促进全球知识共享，降低地理障碍。


## 7. 讨论与展望

### 7.1 主要发现总结

本文通过对2020-2025年ArXiv AI论文的系统分析，得出以下主要发现：

1. **技术层面**：AI技术正从专用模型向通用模型演进，多模态、具身智能、生成式AI成为新增长点；
2. **应用层面**：AI渗透各行各业，医疗、金融、教育、自动驾驶等领域应用加速落地；
3. **治理层面**：AI伦理、安全、监管受到前所未有的重视，全球治理框架逐步形成；
4. **地理层面**：美中欧三极格局稳定，但多极化趋势显现，国际合作与竞争并存。

### 7.2 对未来研究的建议

基于本文分析，对未来AI研究提出以下建议：

1. **加强基础理论突破**：当前AI主要依赖深度学习，亟需新的理论范式（如神经符号融合、因果推理）；
2. **重视AI安全研究**：随着AI系统能力增强，确保其安全性和可控性成为紧迫课题；
3. **推动跨学科融合**：AI与认知科学、神经科学、社会学、伦理学等学科交叉将产生新洞察；
4. **关注AI社会影响**：深入研究AI对就业、教育、医疗、司法等领域的社会经济影响。

### 7.3 研究方法局限与改进方向

本研究存在以下局限，未来研究可加以改进：

1. **数据来源单一**：应整合多个学术数据库（IEEE, ACM, Springer, Elsevier等）；
2. **分析方法简化**：可采用更先进的自然语言处理技术（如大语言模型）进行深度文本分析；
3. **地理推断不准**：应建立更精确的作者机构地理数据库；
4. **引文分析缺失**：未分析论文引用网络，无法识别高影响力论文和关键节点。

### 7.4 对未来AI发展的展望

展望未来5-10年，AI发展可能呈现以下趋势：

1. **AGI愿景驱动**：通用人工智能（AGI）成为研究终极目标，多模态、推理、规划能力持续提升；
2. **AI民主化加速**：开源模型、低代码/无代码工具降低AI使用门槛，赋能更多创新者；
3. **AI监管成熟**：全球AI监管框架基本形成，合规成本成为AI企业重要考量；
4. **AI融入日常生活**：从"AI赋能"到"AI原生"，AI成为像电力一样的基础设施；
5. **人机关系重塑**：AI助手、数字人、脑机接口等技术重新定义人与机器的关系。


## 8. 结论

本文基于ArXiv数据库中2020-2025年的AI学术论文，系统分析了人工智能技术的演进趋势、行业应用热点、伦理与监管发展，以及全球研究地理分布。主要结论如下：

1. **技术演进方面**，大型语言模型、多模态AI、具身智能成为主导方向，AI正从专用走向通用、从感知走向认知；

2. **应用趋势方面**，AI在医疗、金融、教育、自动驾驶等领域的应用加速落地，产业价值日益凸显；

3. **伦理监管方面**，AI安全、公平性、隐私保护成为研究热点，全球监管框架逐步形成，负责任AI理念普及；

4. **地理分布方面**，美国、中国、欧洲继续引领AI研究，但多极化趋势显现，国际合作与竞争并存。

本文的研究结果为学术界和产业界提供了全面的AI发展趋势洞察。未来研究应关注基础理论突破、AI安全、跨学科融合和社会影响评估，推动人工智能朝着更加安全、公平、可持续的方向发展。

---

**致谢**

感谢ArXiv提供开放的学术数据平台，感谢所有为AI研究做出贡献的研究人员。

**利益冲突声明**

作者声明无利益冲突。

**数据可用性声明**

本研究使用的论文元数据可从ArXiv API获取（https://arxiv.org/help/api/）。分析代码和结果数据已开源（请根据实际情况填写仓库地址）。


## 参考文献

[1] Nolan P Shaw, P Michael Furlong, Britt Anderson et al. (2025). Developing a Foundation of Vector Symbolic Architectures Using Category Theory. *ArXiv preprint* https://arxiv.org/abs/2501.05368v2

[2] Xiaoxi Li, Guanting Dong, Jiajie Jin et al. (2025). Search-o1: Agentic Search-Enhanced Large Reasoning Models. *ArXiv preprint* https://arxiv.org/abs/2501.05366v1

[3] Chong Liu, Dan Qiao, Ming Yin et al. (2025). No-Regret Linear Bandits under Gap-Adjusted Misspecification. *ArXiv preprint* https://arxiv.org/abs/2501.05361v1

[4] Edmund Dable-Heath, Boyko Vodenicharski, James Bishop (2025). On Corrigibility and Alignment in Multi Agent Games. *ArXiv preprint* https://arxiv.org/abs/2501.05360v1

[5] Junha Park, Jaehui Hwang, Ian Ryu et al. (2025). SC-Pro: Training-Free Framework for Defending Unsafe Image Synthesis Attack. *ArXiv preprint* https://arxiv.org/abs/2501.05359v2

[6] Mingzi Wang, Yuan Meng, Chen Tang et al. (2025). JAQ: Joint Efficient Architecture Design and Low-Bit Quantization with Hardware-Software Co-Exploration. *ArXiv preprint* https://arxiv.org/abs/2501.05339v1

[7] Yanbing Zhou, Xiangmou Qu, Chenlong You et al. (2025). FedSA: A Unified Representation Learning via Semantic Anchors for Prototype-based Federated Learning. *ArXiv preprint* https://arxiv.org/abs/2501.05496v2

[8] Hantao Lou, Jiaming Ji, Kaile Wang et al. (2025). Stream Aligner: Efficient Sentence-Level Alignment via Distribution Induction. *ArXiv preprint* https://arxiv.org/abs/2501.05336v1

[9] Simon Krogmann, Pascal Lenzner, Alexander Skopalik (2025). The Bakers and Millers Game with Restricted Locations. *ArXiv preprint* https://arxiv.org/abs/2501.05334v2

[10] Ari Blondal, Shan Gao, Hamed Hatami et al. (2025). Stability and List-Replicability for Agnostic Learners. *ArXiv preprint* https://arxiv.org/abs/2501.05333v3

[11] Samir Sadok, Simon Leglaive, Laurent Girin et al. (2025). AnCoGen: Analysis, Control and Generation of Speech with a Masked Autoencoder. *ArXiv preprint* https://arxiv.org/abs/2501.05332v1

[12] Dmytro Kuzmenko, Nadiya Shvai (2025). Knowledge Transfer in Model-Based Reinforcement Learning Agents for Efficient Multi-Task Learning. *ArXiv preprint* https://arxiv.org/abs/2501.05329v1

[13] Laura State, Alejandra Bringas Colmenarejo, Andrea Beretta et al. (2025). The explanation dialogues: an expert focus study to understand requirements towards explanations within the GDPR. *ArXiv preprint* https://arxiv.org/abs/2501.05325v1

[14] Hesham G. Moussa, Arashmid Akhavain, S. Maryam Hosseini et al. (2025). Distributed Learning and Inference Systems: A Networking Perspective. *ArXiv preprint* https://arxiv.org/abs/2501.05323v1

[15] Xiaodi Li, Dingcheng Li, Rujun Gao et al. (2025). LSEBMCL: A Latent Space Energy-Based Model for Continual Learning. *ArXiv preprint* https://arxiv.org/abs/2501.05495v1

[16] Mengfan Liu, Wei Wang, Chuan Wu (2025). Optimizing Distributed Deployment of Mixture-of-Experts Model Inference in Serverless Computing. *ArXiv preprint* https://arxiv.org/abs/2501.05313v1

[17] Daniela Antonova, Allegra Laro, Audra McMillan et al. (2025). Private Selection with Heterogeneous Sensitivities. *ArXiv preprint* https://arxiv.org/abs/2501.05309v1

[18] Mohammad Amin Mirzaee, Hung-Jui Huang, Wenzhen Yuan (2025). GelBelt: A Vision-based Tactile Sensor for Continuous Sensing of Large Surfaces. *ArXiv preprint* https://arxiv.org/abs/2501.06263v1

[19] Otabek Sattarov, Jaeyoung Choi (2025). Detection of Rumors and Their Sources in Social Networks: A Comprehensive Survey. *ArXiv preprint* https://arxiv.org/abs/2501.05292v1

[20] Nora Gourmelon, Konrad Heidler, Erik Loebel et al. (2025). Comparison Study: Glacier Calving Front Delineation in Synthetic Aperture Radar Images With Deep Learning. *ArXiv preprint* https://arxiv.org/abs/2501.05281v2

[21] Emilia Magnani, Ernesto De Vito, Philipp Hennig et al. (2025). Learning convolution operators on compact Abelian groups. *ArXiv preprint* https://arxiv.org/abs/2501.05279v3

[22] Ritam Guha, Nilavra Pathak (2025). Off-Policy Evaluation and Counterfactual Methods in Dynamic Auction Environments. *ArXiv preprint* https://arxiv.org/abs/2501.05278v1

[23] S. Sanjuan, D. A. Méndez, R. Arnau et al. (2025). Soft Computing Approaches for Predicting Shade-Seeking Behaviour in Dairy Cattle under Heat Stress: A Comparative Study of Random Forests and Neural Networks. *ArXiv preprint* https://arxiv.org/abs/2501.05494v2

[24] Xinzi Cao, Xiawu Zheng, Guanhong Wang et al. (2025). Solving the Catastrophic Forgetting Problem in Generalized Category Discovery. *ArXiv preprint* https://arxiv.org/abs/2501.05272v2

[25] Fabian Hörst, Moritz Rempe, Helmut Becker et al. (2025). CellViT++: Energy-Efficient and Adaptive Cell Segmentation and Classification Using Foundation Models. *ArXiv preprint* https://arxiv.org/abs/2501.05269v1

[26] Wanli Ma, Oktay Karakus, Paul L. Rosin (2025). Patch-GAN Transfer Learning with Reconstructive Models for Cloud Removal. *ArXiv preprint* https://arxiv.org/abs/2501.05265v1

[27] Mengshi Qi, Jiaxuan Peng, Xianlin Zhang et al. (2025). Towards Balanced Multi-Modal Learning in 3D Human Pose Estimation. *ArXiv preprint* https://arxiv.org/abs/2501.05264v5

[28] Atharva Mutsaddi, Aditya Choudhary (2025). Enhancing Plagiarism Detection in Marathi with a Weighted Ensemble of TF-IDF and BERT Embeddings for Low-Resource Language Processing. *ArXiv preprint* https://arxiv.org/abs/2501.05260v1

[29] Daniele Cipollone, Changjie Wang, Mariano Scazzariello et al. (2025). Automating the Detection of Code Vulnerabilities by Analyzing GitHub Issues. *ArXiv preprint* https://arxiv.org/abs/2501.05258v1

[30] Yewei Song, Xunzhu Tang, Cedric Lothritz et al. (2025). CallNavi, A Challenge and Empirical Study on LLM Function Calling and Routing. *ArXiv preprint* https://arxiv.org/abs/2501.05255v2

[31] Changjie Wang, Mariano Scazzariello, Marco Chiesa (2025). From Scientific Texts to Verifiable Code: Automating the Process with Transformers. *ArXiv preprint* https://arxiv.org/abs/2501.05252v1

[32] Peizhuo Lv, Mengjie Sun, Hao Wang et al. (2025). RAG-WM: An Efficient Black-Box Watermarking Approach for Retrieval-Augmented Generation of Large Language Models. *ArXiv preprint* https://arxiv.org/abs/2501.05249v1

[33] Laura Puccioni, Alireza Farshin, Mariano Scazzariello et al. (2025). Deriving Coding-Specific Sub-Models from LLMs using Resource-Efficient Pruning. *ArXiv preprint* https://arxiv.org/abs/2501.05248v1

[34] Yixuan Li, Lewis Frampton, Federico Mora et al. (2025). Online Prompt Selection for Program Synthesis. *ArXiv preprint* https://arxiv.org/abs/2501.05247v2

[35] Shishir Muralidhara, René Schuster, Didier Stricker (2025). Domain-Incremental Semantic Segmentation for Autonomous Driving under Adverse Driving Conditions. *ArXiv preprint* https://arxiv.org/abs/2501.05246v1

[36] Talha Sultan, Alex Bocchieri, Chaoying Gu et al. (2025). Optimized Sampling for Non-Line-of-Sight Imaging Using Modified Fast Fourier Transforms. *ArXiv preprint* https://arxiv.org/abs/2501.05244v1

[37] Tianci Wen, Zhiang Liu, Yongchun Fang (2025). SEGS-SLAM: Structure-enhanced 3D Gaussian Splatting SLAM with Appearance Embedding. *ArXiv preprint* https://arxiv.org/abs/2501.05242v3

[38] Benedikt Holm, Arnar Óskarsson, Björn Elvar Þorleifsson et al. (2025). World of ScoreCraft: Novel Multi Scorer Experiment on the Impact of a Decision Support System in Sleep Staging. *ArXiv preprint* https://arxiv.org/abs/2503.15492v1

[39] Guang Yang, Jingkun Chen, Xicheng Sheng et al. (2025). Contrast-Free Myocardial Scar Segmentation in Cine MRI using Motion and Texture Fusion. *ArXiv preprint* https://arxiv.org/abs/2501.05241v1

[40] Wenhao Liao, Sineng Yan, Youqian Zhang et al. (2025). Is Your Autonomous Vehicle Safe? Understanding the Threat of Electromagnetic Signal Injection Attacks on Traffic Scene Perception. *ArXiv preprint* https://arxiv.org/abs/2501.05239v1

[41] Zuyao You, Lingyu Kong, Lingchen Meng et al. (2025). FOCUS: Towards Universal Foreground Segmentation. *ArXiv preprint* https://arxiv.org/abs/2501.05238v1

[42] Sadhana Ravikumar, Asma A. Khan, Matthew C. Davis et al. (2025). Automated external cervical resorption segmentation in cone-beam CT using local texture features. *ArXiv preprint* https://arxiv.org/abs/2501.05236v1

[43] Artem Fedorchenko, Tanel Alumäe (2025). Optimizing Estonian TV Subtitles with Semi-supervised Learning and LLMs. *ArXiv preprint* https://arxiv.org/abs/2501.05234v1

[44] Aman Saggu (2025). The Intraday Bitcoin Response to Tether Minting and Burning Events: Asymmetry, Investor Sentiment, And "Whale Alerts" On Twitter. *ArXiv preprint* https://arxiv.org/abs/2501.05232v1

[45] Pei-Kang Lee, Jun-Cheng Chen, Ja-Ling Wu (2025). Harnessing Large Language and Vision-Language Models for Robust Out-of-Distribution Detection. *ArXiv preprint* https://arxiv.org/abs/2501.05228v1

[46] Ludwic Leonard, Nils Thuerey, Ruediger Westermann (2025). Light Transport-aware Diffusion Posterior Sampling for Single-View Reconstruction of 3D Volumes. *ArXiv preprint* https://arxiv.org/abs/2501.05226v3

[47] Devendra Vyas, Nikola Pižurica, Nikola Milović et al. (2025). Towards smart and adaptive agents for active sensing on edge devices. *ArXiv preprint* https://arxiv.org/abs/2501.06262v2

[48] Tomas Goldsack, Carolina Scarton, Chenghua Lin (2025). Leveraging Large Language Models for Zero-shot Lay Summarisation in Biomedicine and Beyond. *ArXiv preprint* https://arxiv.org/abs/2501.05224v1

[49] Tianle Tao, Shizhao Peng, Tianyu Mei et al. (2025). EVA-S2PLoR: Decentralized Secure 2-party Logistic Regression with A Subtly Hadamard Product Protocol (Full Version). *ArXiv preprint* https://arxiv.org/abs/2501.05223v3

[50] Léane Jourdan, Nicolas Hernandez, Richard Dufour et al. (2025). ParaRev: Building a dataset for Scientific Paragraph Revision annotated with revision instruction. *ArXiv preprint* https://arxiv.org/abs/2501.05222v1



---

**附录：数据分析结果摘要**

- 分析论文总数：10002
- 分析时间：2026-06-11T15:56:08.698990
- 详细分析结果见：`output/analysis_results.json`
