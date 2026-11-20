Grounded Adaptive Course — Living Spec
MVP purpose
Grounded Tutor is a seeded, instructor-approved “Intro to Data Structures” workspace. It provides source-cited explanations, a classical retrieval baseline, optional compact-LLM generation, formative quizzes with a four-point rubric, lightweight progress tracking, safe next-topic suggestions, instructor guardrail controls, and an evaluation/ablation dashboard.

Data model
topics: five course topics with difficulty, mastery, and lesson counts.
source_chunks: approved slide/notes/rubric passages used for overlap-ranked retrieval.
progress: minimal demo-student topic attempts and mastery deltas.
course_settings: instructor step limits and answer-leakage controls.
course_meta: idempotent seed marker.
Key flows
Student opens Tutor Workspace, chooses a topic, asks a question, sees a grounded answer, citations, confidence, tool trace, and next topic.
Student opens Formative Quiz, generates a topic question, selects an option, receives rubric criteria and a next-topic recommendation.
Instructor opens Control Tower, changes max turns/scaffolding/guardrails, and sees approval status.
Evaluation view shows Recall@k, citation precision, rubric agreement, refusal rate, latency, ablations, and safety probes.
Academic misconduct and prompt injection patterns are refused with a safe redirect to concept help or practice.
Auth and roles
Emergent-managed Clerk is provisioned for email/password. The preview demo remains readable without sign-in so the core course can be evaluated; the Clerk sign-in and sign-up routes are available from the header. Instructor controls are presented as the demo instructor view; production role enforcement should be connected to the app user record after an instructor email is selected.

Integrations
The optional tutor generation path uses the Emergent Universal LLM key with gpt-5.4-mini through emergentintegrations; the default UI uses the deterministic grounded baseline for predictable preview behavior. The frontend labels the active pipeline and whether a response used the compact LLM.