### Comprehensive Briefing Document: Multi-Objective Deep Reinforcement Learning and Cloud-Edge Multi-Agent Digital Twin Architectures

#### Executive Summary

This briefing document provides an in-depth synthesis of research in advanced artificial intelligence and industrial automation, focusing on two core domains:  **Multi-Objective Deep Reinforcement Learning (MODRL)**  and  **Multi-Agent Cloud-Edge Orchestration of Digital Twins (DT)** .

1. **Multi-Objective Deep Reinforcement Learning (MODRL)** : Traditional Multi-Objective Reinforcement Learning (MORL) relies on tabular methods like Q-learning, which suffer from memory explosion ( \$O(n^2)\$  memory growth) and cannot handle high-dimensional or image-based inputs. The MODRL framework developed by Thanh Thi Nguyen addresses these limitations by integrating Deep Q-Networks (DQN) with vector reward structures, supporting scalar, vector, and visual state inputs via TensorFlow. It introduces single-policy (linear scalarization and non-linear Thresholded Lexicographic Ordering) and multi-policy parallel multi-threaded strategies to discover non-dominated Pareto-optimal solutions across complex problem spaces.  
2. **Cloud-Edge & Multi-Agent Digital Twin Orchestration** : Modern smart manufacturing requires real-time responsiveness, flexibility, and scalability to manage mass individualization, small-batch production, and dynamic operational disturbances. Pure cloud architectures incur latency and bandwidth bottlenecks, while pure edge deployments lack computational capacity for complex analytics. Recent frameworks—exemplified by Nie et al., Leng et al., and related literature—combine Multi-Agent Systems (MAS) and Digital Twin (DT) technology across hierarchical Cloud-Edge continuums. This enables low-latency deterministic execution at the edge and global, compute-intensive optimization at the cloud.

#### Section 1: Multi-Objective Deep Reinforcement Learning (MODRL) Framework

##### 1.1 Context and Technical Motivation

In standard single-objective reinforcement learning, an agent learns to optimize a scalar reward. However, real-world problems frequently demand balancing multiple competing goals (e.g., maximizing speed while minimizing energy consumption).  
Prior approaches faced critical bottlenecks:

* **Memory Inefficiency of Tabular Methods** : Classical tabular Q-learning requires memory scaling at  \$O(n^2)\$ , where  \$n\$  is the state space dimension. For example, in the Deep Sea Treasure (DST) benchmark, tabular Q-learning fails when the environment exceeds 10,000 columns due to requiring over 1.6 GB of memory.  
* **Input State Limitations** : Frameworks such as MORL\_Glue only support simple integer or continuous state vectors and cannot process high-dimensional visual inputs (e.g., camera images).  
* **Concave Pareto Boundaries** : Simple linear scalarization of vector rewards cannot converge to optimal policies located in concave regions of the Pareto front.

The generic Python/TensorFlow MODRL framework developed by Thanh Thi Nguyen resolves these challenges by replacing tabular representations with deep neural networks and experience replay mechanisms, enabling low-memory processing of scalar, vector, and image inputs.

##### 1.2 Algorithmic Strategies

The framework supports both single-policy and multi-policy learning strategies using linear and non-linear mechanisms.  
                  ┌─────────────────────────────────────────┐  
                  │        MODRL Framework (DQN)            │  
                  └────────────────────┬────────────────────┘  
                                       │  
            ┌──────────────────────────┴──────────────────────────┐  
            ▼                                                     ▼  
┌──────────────────────┐                               ┌──────────────────────┐  
│ Single-Policy Strategy│                               │ Multi-Policy Strategy│  
└───────────┬──────────┘                               └───────────┬──────────┘  
            │                                                      │  
     ┌──────┴──────────────────────┐                               │  
     ▼                             ▼                               ▼  
┌─────────┐                ┌──────────────┐             ┌─────────────────────┐  
│ Linear  │                │ Non-Linear   │             │ Multi-Threaded      │  
│ Scalarization            │ (TLO \+ Linear)│             │ Parallel Learning   │  
└─────────┘                └──────────────┘             └─────────────────────┘

###### *1\. Single-Policy Linear DQN*

The linear approach scalarizes vector rewards using a fixed weight vector  \$\\mathbf{w} \= \\{w\_1, w\_2, \\dots, w\_n\\}\$  that represents the relative priority of each objective. Given a reward vector  \$\\mathbf{r} \= \\{r\_1, r\_2, \\dots, r\_n\\}\$ , the loss function  \$L(\\theta)\$  for the DQN is defined as:  
\$\$L(\\theta) \= \\mathbb{E} \\left\\left( \\sum\_{i=1}^{n} w\_i r\_i \+ \\gamma \\max\_{a'} Q(s', a'; \\theta') \- Q(s, a; \\theta) \\right)^2 \\right\$\$  
*Where:*

* \$\\gamma\$  is the discount rate ( \$0 \\le \\gamma \\le 1\$ ).  
* \$s\$  and  \$s'\$  represent current and next states.  
* \$a\$  and  \$a'\$  represent current and next actions.  
* \$\\theta\$  and  \$\\theta'\$  represent weights of the estimation and target networks, respectively.

*Limitation* : Linear scalarization cannot reach solutions located in non-convex or concave regions of the Pareto front regardless of the weight vector chosen.

###### *2\. Single-Policy Non-Linear DQN (TLO \+ Linear)*

To access non-convex Pareto solutions, the framework combines  **Thresholded Lexicographic Ordering (TLO)**  with linear scalarization.

* Thresholds are applied to the first  \$n-1\$  objectives based on expected minimum and maximum values.  
* Values exceeding the threshold are truncated, preventing dominant objectives from obscuring intermediate Pareto solutions.  
* Linear scalarization is then applied to the thresholded objective outputs.

###### *3\. Multi-Policy Parallel DQN*

In dynamic real-world environments, user preferences over competing objectives change over time. Single-policy methods force the agent to retrain from scratch whenever preference weights shift.

* The MODRL framework executes  **multi-threaded parallel training** , assigning independent thread agents to learn different policies across the weight space simultaneously.  
* This pre-computes an approximation of the complete Convex Coverage Set (CCS) / Pareto front, allowing instant policy switching during runtime without retraining delays.

##### 1.3 Empirical Evaluation: Deep Sea Treasure (DST) Benchmark

The framework was evaluated using the Deep Sea Treasure (DST) benchmark environment. In DST, an agent controls a submarine searching for treasure.

* **Objective 1** : Maximize treasure value (positive reward obtained upon reaching treasure).  
* **Objective 2** : Minimize search time (time penalty of  \$-1\$  per action step).  
* **Actions** : 4 movement directions (up, down, left, right).  
* **State Inputs** : Evaluated using both position vectors/scalars and raw visual image representations.

(0,0) Submarine Start  
  ┌───┬───┬───┐  
  │ S │   │   │  
  ├───┼───┼───┤  Row 1 (Treasure \= 1, Penalty \= \-3)  
  │ T1│   │   │  
  ├───┴───┼───┤  Row 2 (Treasure \= 26.25, Penalty \= \-5)  
          │ T2│  
          └───┤  Row 3 (Treasure \= 100, Penalty \= \-7)  
              │ T3│  
              └───┘

###### *Results across Environmental Widths*

Environment,Columns,"Optimal Pareto Solutions (Treasure Value, Time Penalty)",Key Performance Insights  
DST 3-Column,3,"\$(1, \-3)\$ ,  \$(26.25, \-5)\$ ,  \$(100, \-7)\$","• Linear DQN with weights  \$0.01, 1\$  finds  \$(1, \-3)\$  in 200,000 steps. • Solution  \$(26.25, \-5)\$   cannot  be found by linear weights  \$a, b\$  for any  \$a,b \> 0\$ . Using TLO threshold of 20 with weights  \$100, 1\$  successfully converges to  \$(26.25, \-5)\$ . • Multi-threaded agents learn all 3 solutions in parallel in \~200,000 steps (\~2x faster than sequential single-agent search at \~400,000 steps)."  
DST 5-Column,5,"\$(1, \-3)\$ ,  \$(5, \-5)\$ ,  \$(17, \-7)\$ ,  \$(49, \-10)\$ ,  \$(100, \-13)\$","• Solution  \$(1, \-3)\$  isolated via linear scalarization. • Solutions 2–5 isolated via non-linear TLO thresholding."  
DST 7-Column,7,"\$(1, \-3)\$ ,  \$(2, \-5)\$ ,  \$(7, \-7)\$ ,  \$(19, \-10)\$ ,  \$(39, \-13)\$ ,  \$(65, \-16)\$ ,  \$(100, \-19)\$",• Successfully converges across all 7 Pareto points. • Pareto approximation difference drops to zero as learning completes.

###### *Hyperparameter Configuration Settings*

Parameter,Value,3-Column,5-Column,7-Column  
Hidden Layers,"2 layers ( \$512 \\times 512\$  units, ReLU) / Conv layers for images",—,—,—  
Initial / Final Epsilon,\$1.0 \\to 0\$,—,—,—  
Learning Rate,\$0.0001\$,—,—,—  
Discount Rate (  \$\\gamma\$  ),\$0.9\$,—,—,—  
Target Update Interval,"\$1,000\$  steps",—,—,—  
Optimizer,"RMSprop (decay \=  \$0.99\$ ,  \$\\epsilon \= 10^{-6}\$ )",—,—,—  
Epsilon Annealing Steps,—,"\$200,000\$","\$500,000\$","\$2,000,000\$"  
Experience Replay Size,—,"\$100,000\$","\$200,000\$","\$300,000\$"  
Warmup Steps,—,"\$10,000\$","\$20,000\$","\$30,000\$"  
Training Epochs,"\$100,000\$  steps per epoch",\$2\$,\$5\$,\$20\$

#### Section 2: Multi-Agent and Cloud-Edge Orchestration of Digital Twins

##### 2.1 Industrial Context and Problem Framing

Modern manufacturing systems face rising demand for  **mass individualization** , short production runs, and rapid response to unexpected shop-floor disturbances (equipment breakdown, material defects, or rush orders).  
Deploying centralized or single-tier architectures creates operational bottlenecks:

* **Cloud-Only Architectures** : Suffer from network latency, jitter, bandwidth consumption, and security risks, making them unsuitable for real-time hard-interlock machine control.  
* **Edge-Only Architectures** : Constrained by local compute power and storage, preventing high-fidelity simulation, global optimization, or long-term historical trend modeling.

To bridge this gap, research by Nie et al. (2023) and supporting studies establishes a  **Multi-Agent and Cloud-Edge Orchestration Framework of Digital Twins (DT)** .

##### 2.2 Functional Architecture of Cloud-Edge DT Systems

The cloud-edge continuum divides responsibilities across functional layers to combine low-latency local execution with continuous global optimization:  
┌─────────────────────────────────────────────────────────────────────────┐  
│                               CLOUD LAYER                               │  
│  • Global Optimization & Analytics   • High-Fidelity Simulation Twins   │  
│  • Deep Learning / Model Training    • Long-Term Historical Data        │  
└────────────────────────────────────┬────────────────────────────────────┘  
                                     │ Synchronization & Feedback  
                                     ▼  
┌─────────────────────────────────────────────────────────────────────────┐  
│                                EDGE LAYER                               │  
│  • Distributed Autonomous Agents     • Real-time Exception Response     │  
│  • Local Process Control & HMI       • Deterministic Execution          │  
└────────────────────────────────────┬────────────────────────────────────┘  
                                     │ Low-Latency Direct Interlock  
                                     ▼  
┌─────────────────────────────────────────────────────────────────────────┐  
│                             PHYSICAL LAYER                              │  
│  • CNC Machine Tools  • AGVs / Industrial Robots  • IIoT Sensors        │  
└─────────────────────────────────────────────────────────────────────────┘

###### *Layer Responsibilities & Capabilities*

* **Cloud Tier (Global & Asynchronous)** :  
* Operates on long timescales.  
* Manages heavy computational tasks: deep neural network training (e.g., Bi-LSTM, CNNs), global rescheduling, historical trend analytics, and high-fidelity virtual twin simulations.  
* Feeds updated optimization policies, parameters, and predictive models down to edge units.  
* **Edge Tier (Local & Deterministic)** :  
* Operates on fast, real-time timescales close to physical assets.  
* Deploys autonomous  **Multi-Agent Systems (MAS)**  representing machines, workpieces, AGVs, or processes.  
* Executes low-latency monitoring, immediate anomaly classification, and dynamic local conflict resolution.  
* **Physical / End Tier** :  
* Industrial equipment (CNC machine tools, automated fiber placement units, assembly lines, sensors).  
* Executes control commands issued by edge agents while streaming operational telemetry back to edge and cloud digital twins.

##### 2.3 Key Scientific and Engineering Breakthroughs

Research across multi-agent cloud-edge digital twin systems reveals several key architectural paradigms:

* **Bi-Level Autonomous Process Control (CEO-BAPC)** :  
* *Edge* : Blockchain smart contracts and multi-agent coordination (e.g., Stackelberg game solutions) autonomously handle short-term, fine-grained task execution under random disturbances.  
* *Cloud* : Deep learning models process edge-collected event data to generate global, macro-level rescheduling decisions (Leng et al., 2022).  
* **Multi-Agent Exception Handling & Self-Adaptation** :  
* Distributed agents use localized decision rules (e.g., Double DQN or heuristic conflict resolution) to handle minor deviations without halting the shop floor.  
* Real-time shop-floor exceptions update the local DT model, which triggers cloud-level global adjustments only when thresholds are exceeded (Nie et al., 2023; Chen et al., 2025).  
* **Resource Optimization via Avian/Swarm Algorithms** :  
* Algorithms like the Swarm Avian Evolutionary Algorithm (combining PSO and meta-heuristics) map edge agents to physical manufacturing resources over 5G networks, drastically minimizing computation times and increasing response speed (Zhu et al., 2025).  
* **End-Edge-Cloud Decision Support for Specialized Manufacturing** :  
* Applied in Automated Fiber Placement (AFP), edge models process temporal-statistical features for real-time anomaly classification and cutter Remaining Useful Life (RUL) estimation while maintaining hard safety interlocks (Guo et al., 2026).

#### Section 3: Comparative Architectural Synthesis

The table below summarizes the key trade-offs, scope, and operational profiles of the methods analyzed in this briefing:  
Dimension,Single-Policy Linear MODRL,Single-Policy Non-Linear MODRL (TLO),Multi-Policy Parallel MODRL,Cloud-Edge Digital Twin Orchestration  
Core Objective,Single optimal policy under fixed scalar weights,Target specific non-convex/concave Pareto points,Approx. full Convex Coverage Set (CCS) in parallel,Real-time distributed control & global optimization  
Primary Mechanism,Linear weighted sum of vector rewards,Lexicographic thresholding \+ linear scalarization,Multi-threaded agents learning unique weight vectors,Cloud-based deep learning \+ Edge Multi-Agent Systems  
Computational Footprint,Low ( \$O(1)\$  agent models during inference),Low ( \$O(1)\$  agent models during inference),Moderate to High (proportional to thread count),Distributed across edge nodes and cloud servers  
Runtime Adaptability,Poor (requires complete retraining if weights shift),Poor (requires threshold adjustment & retraining),High (instant switching across pre-trained policies),High (handles dynamic shop-floor disturbances)  
Target Applications,Fixed-priority multi-objective tasks,"Non-convex trade-offs (e.g., DST solution  \$(26.25, \-5)\$ )",Dynamic real-time preference shifts,"Smart manufacturing, PCB prototyping, AFP, building energy"

#### Section 4: Key Insights and Summary Takeaways

1. **Deep Methods Solve the Scalability Bottleneck** : Integrating Deep Q-Networks into multi-objective reinforcement learning eliminates the  \$O(n^2)\$  memory constraints of tabular Q-learning, allowing reinforcement learning to scale to environments with high-dimensional continuous or image-based state spaces.  
2. **Non-Linear Techniques are Essential for Concave Pareto Fronts** : Standard linear weight scalarization fails to reach non-convex regions of a Pareto boundary. Combining Thresholded Lexicographic Ordering (TLO) with linear weights effectively uncovers non-dominated intermediate solutions.  
3. **Parallel Multi-Threading Accelerates Convergence** : Training multiple single-policy agents concurrently across different CPU threads yields a 2x convergence speedup compared to sequential search, while producing a full set of operational policies ready for dynamic deployment.  
4. **Cloud-Edge DT Orchestration Balances Latency and Intelligence** : Coupling Multi-Agent Systems at the edge with cloud-based analytics solves the trade-off between real-time responsiveness and deep computation, enabling resilient, autonomous, and self-adaptive control in modern industrial ecosystems.

