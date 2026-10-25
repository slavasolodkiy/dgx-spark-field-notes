# One Spark. Two experiences. One owner — and an AI operator.

Slava Solodkiy · 25 October 2026

This product field note accompanies the measured DGX OS → OlaresOS case. It is my interpretation of hands-on experience, not a better/worse scorecard.


## Two installations. Two different experiences.

I was not starting from zero. I had already used Olares One and installed OlaresOS on other machines. Spark let me ask a more useful question: what changes for the same owner, with the same goal, on the same hardware?


### A polished first boot. A developer-shaped way in.

The native setup and the NVIDIA-themed desktop made a good first impression. The first mistake was mine: Spark had powered on when I connected it, and an extra press of Power turned it off. A short explanation from my AI assistant resolved what had looked like a mysterious wait.

With a physical console I reached the actual Ubuntu desktop. Remotely, NVIDIA Sync, SSH, Dashboard and Tailscale got me productive. But the Dashboard was not the same thing as seeing and controlling that Ubuntu desktop. I stopped before configuring a streamed native desktop: for me, at that moment, it was one more layer to assemble.

Owner observation · This is where I stopped, not a claim that remote desktop is impossible. NVIDIA Sync's documented scope ↗


### A familiar destination. A harder installation here.

I recognised the installation and activation flow from earlier Olares machines. That familiarity did not make this Spark installation smooth: Secure Boot rejected the driver module, the incomplete driver broke GPU readiness, and an activation TLS error added another interruption.

Once repaired and activated, the result was closer to the environment I had wanted: my Olares profile, browser Desktop, apps and Control Hub. A Windows ARM64 VM then gave my desktop AI operator a familiar place to work, reached through its web console or Chrome Remote Desktop.

Owner observation · Olares Desktop is a web workspace; the Windows console is a guest desktop. Neither is a 1:1 stream of the Linux host's physical display.


### User-friendly is only half the question.

The next owner may arrive with an AI assistant already open. My product question is whether the computer is prepared for that assistant to discover its state, obtain the right access, install a capability, diagnose a failure and return the result — instead of asking the owner to relay every command.

In this run the operator did substantial work over SSH and through application interfaces. That was real progress, not a reason to discard terminal access. The wider opportunity is a coherent path across shell, browser and GUI, with fewer handoffs left for the owner to improvise.

My earliest Olares experience used chat guidance without the desktop operator available during this Spark run. Familiarity and better assistance both changed the experience; these are field observations, not a timed usability trial.

NVIDIA's current Spark guide describes reusable agent skills for maintenance and troubleshooting. I treat that as relevant product direction, separate from what we actually exercised in this run. NVIDIA documentation ↗


## Can I reach my computer? Who else can — and as whom?

A working remote connection answers only part of the personal-computer question. I also want a legible relationship between me, my devices, other people and the agents acting for us.

Question | DGX OS + Sync path | OlaresOS + LarePass path

Where does my identity enter? | In my setup: a local Linux user and SSH credentials; Sync kept the connection profile; Tailscale supplied the remote-network identity. I did not encounter a single owner-linked identity flow joining all of these. | I created an Olares ID, activated the system with LarePass and received a personal Desktop address. Identity, activation and the web workspace appeared as parts of the same experience.

What about several devices? | Sync documents adding and importing multiple device connections, not just one Spark. Its Tailscale integration supports access beyond the local network. | LarePass documents multiple Olares IDs, account switching and importing an identity on other clients. In my lab, a separate Spark profile joined that familiar pattern. Several profiles in one client are not the same thing as one person-level fleet identity.

How could another person get access? | Tailscale documents sharing individual machines, governed by access policies. Device reachability and permission to log into the OS or use an application remain distinct layers. | Olares documents Super Admin, Admin and Member roles, plus authentication policies for application entrances. These are existing product controls, not just a future wish.

What did this run exercise? | My own remote access through Sync/SSH and Tailscale. I did not run a second-person delegation or revocation test. | My profile, activation, authenticated browser access and app operation. Team roles and sharing are documented context, not a multi-user acceptance test from this run.

Architecture references: NVIDIA Sync · Sync + Tailscale · Tailscale sharing · Olares ID · LarePass accounts · Roles · App access .

Olares made more of that relationship visible in the interface I used. The NVIDIA path exposed capable, composable layers. My interest is not to declare one architecture the winner, but to see how little of their assembly the next owner has to do.

The next design step is delegation: let another person — or my AI agent — use an app or a capability without inheriting my entire session. Login, network access and an agent's authority to act are related, but they are not interchangeable.


## Personal need not mean portable.

After hearing Jensen Huang in London on 14 October, I wrote about a shift: first we went to the computer, then carried it, and next we might simply reach it.

That was my recollection and interpretation, not a transcript. My earlier piece connected remote personal computing with a second question: perhaps I own the machine; perhaps someone shares theirs. Can I use the capability under clear permissions without borrowing their private life along with the GPU?

In a later note, I explored the difference between using a tool and being able to build the tool through which work gets done. This Spark run made those ideas concrete: the assistant helped set up the working environment, operate it and repair it. The important product question became how much of that journey the device had already made easy for the owner and the assistant.


## Sources

- sync: https://docs.nvidia.com/sync/latest/index.html
- sync_direct: https://docs.nvidia.com/sync/latest/direct-connections.html
- tailscale: https://docs.nvidia.com/sync/latest/tailscale.html
- sharing: https://tailscale.com/docs/features/sharing
- oid: https://www.olares.com/docs/developer/concepts/olares-id
- accounts: https://www.olares.com/docs/manual/larepass/manage-accounts
- roles: https://www.olares.com/docs/manual/olares/settings/roles-permissions
- entrances: https://www.olares.com/docs/manual/olares/settings/manage-entrance
- spark_iso: https://www.olares.com/docs/manual/get-started/install-spark-iso
- skills: https://docs.nvidia.com/dgx/dgx-spark/nvidia-sync.html
- london: https://slavasolodkiy.substack.com/p/listening-to-jensen-in-berlin-tomorrow
- questions: https://medium.com/@slavasolodkiy_67243/the-tool-is-no-longer-the-bottleneck-the-question-might-be-4abcbb86cdd7


For the complete set of author-provided public posts, see [PUBLIC_WRITING.md](PUBLIC_WRITING.md).
