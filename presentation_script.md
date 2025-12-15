# 5-Minute Poster Presentation Script
## Digital Contagion Simulator

---

**[0:00-0:30] Opening & Hook**

Good morning/afternoon! I'm [Your Name] from Team Brainwave Storms. Have you ever noticed how stress seems to spread through a classroom during exam season? One stressed friend posts about their anxiety, and suddenly everyone's feeling it. We wanted to understand this scientifically, so we built a Digital Contagion Simulator—essentially a "digital twin" of a social network to study how stress spreads like a virus.

---

**[0:30-1:15] The Problem & Approach**

The key question we asked was: If stress spreads through social connections, can we stop it by targeting just a few highly connected people? Think of it like vaccination—you don't need to vaccinate everyone if you vaccinate the right people.

We approached this using Agent-Based Modeling. Instead of guessing, we used real data from 700 smartphone users and ran mathematical simulations. We created 100 synthetic agents—digital people—who interact in a social network for 30 days, and we tracked how their stress levels spread.

---

**[1:15-2:00] The Digital Twin Construction**

Let me show you how we built this. *[Point to network topology graph]* This is our social network—100 nodes, 270 connections. But these aren't random connections. We used K-Means clustering on real smartphone usage data to identify 5 distinct user types: Minimalists who barely use their phones, Moderate users, Active users, Heavy users, and Digital Addicts who are on their phones 10+ hours a day.

Then we connected them using a Stochastic Block Model with an assortativity of 0.426. That's a fancy way of saying "birds of a feather flock together"—addicts connect mostly with other addicts, mimicking real social bubbles.

---

**[2:00-2:45] The Mathematical Engine**

The heart of our model is this stress equation. *[Point to equation]* Every day, each agent's stress is calculated from three factors:

First, their personal phone usage—that's 60% of the equation because your own behavior matters most. Second, peer influence—we average their friends' stress and that contributes 30%, based on research showing stress spreads at about that rate in real social networks. Third, resilience acts as a protective buffer, reducing stress by 10%.

But here's the clever part: we added a feedback loop. If you're stressed today, the model forces you to doomscroll more tomorrow, which increases your stress further. This creates a vicious cycle we see in real life.

---

**[2:45-3:30] The Intervention Experiment**

So here's what we tested. *[Point to comparison graphs]* On Day 10, we identified the top 5 influencers—the people with the most connections—and we "quarantined" them. We forced their screen time down by 50% and reduced how much stress they could broadcast to others by 70%.

The results? *[Point to results table]* The network's average stress dropped by 5.9%, from 42.61 to 40.09. The system also stabilized 1.6 days faster. We ran this 5 times with different random seeds to make sure it wasn't a fluke—the effect was consistent and statistically significant.

---

**[3:30-4:15] The Paradoxes & Complex Findings**

But this is where it gets really interesting. We discovered something unexpected—the Targeting Paradox. *[Point to paradox graph]* When we compared three strategies—targeting influencers, random people, or isolated users—we found that targeting influencers was best for average stress but worst for burnout cases. Burnout actually increased by 12.5%.

Why? Because influencers act as social support hubs. When we "quarantine" them, their dependent friends lose that connection, causing localized stress spikes that push vulnerable people over the edge. It's like removing the popular kid from school—everyone connected to them suffers.

We also tested extreme scenarios. *[Point to echo chamber graph]* In a highly conformist environment where peer pressure dominates—think high school—targeting influencers became massively effective, cutting stress by 65%. But in our base model with weaker peer influence, a universal "Digital Detox Day" where everyone reduced usage was 5 times more effective than targeting just the influencers.

---

**[4:15-4:45] Real-World Implications**

So what does this mean for real campus wellness programs? Our findings suggest that hybrid strategies work best. Use network analysis to identify influencers, yes, but combine that with population-wide policies like mandatory screen-free hours or digital wellness workshops. You can't just target the "super-spreaders" and call it done—the network fights back.

The timing matters too. *[Point to timing graph]* Even late intervention at Day 25 still achieved a 7% reduction, which means it's never too late to implement stress-reduction programs.

---

**[4:45-5:00] Closing & Validation**

To wrap up: we validated our model against real smartphone data with less than 5% error. We proved that stress spreads through networks with measurable dynamics, and that targeted interventions work but have complex trade-offs. The code is open-source on GitHub *[point to QR code]*, and we've documented everything in our technical report.

Are there any questions about the methodology, the mathematical model, or the policy implications?

---

### Quick Response Prep for Common Questions:

**Q: Is your data real?**
A: Yes, we used the Valakhorasani dataset with 700 real smartphone users from Kaggle, then created synthetic agents that statistically match that real data.

**Q: Why did you choose those specific parameter values (α=0.6, β=0.3)?**
A: α=0.6 comes from literature showing personal behavior is the primary stress driver. β=0.3 comes directly from Christakis & Fowler's 2008 study on social contagion in the Framingham Heart Study—they found emotions spread at about 30% transmission rate.

**Q: What are the limitations?**
A: Three main ones: We used a static network that doesn't change over time. We modeled stress transmission as linear when it might be more complex. And we used synthetic data that needs validation with real longitudinal student health data.

**Q: How long did this take?**
A: About [X weeks/months]. The data analysis and clustering took [timeframe], building the simulation engine took [timeframe], and running all the experiments with statistical validation took [timeframe].

**Q: What's next?**
A: We want to test non-linear contagion models, add dynamic network formation where friendships change, test combined interventions like detox plus resilience training, and calibrate with real campus health data.
