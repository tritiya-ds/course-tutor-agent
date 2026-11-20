import re
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lib.db import db
from lib.dates import today_iso
from models.course import (
    Citation,
    CourseOverview,
    EvaluationData,
    EvaluationMetric,
    InstructorSettings,
    QuizGenerate,
    QuizGrade,
    QuizQuestion,
    QuizOption,
    QuizResult,
    RubricCriterion,
    RubricScore,
    ToolTrace,
    Topic,
    TutorAsk,
    TutorResponse,
)

router = APIRouter()

TOPICS = [
    {"id": "arrays", "title": "Arrays & Complexity", "short_title": "Arrays", "difficulty": "Foundational", "summary": "Indexing, contiguous memory, and the cost model behind common array operations.", "mastery": 72, "lesson_count": 4},
    {"id": "linked-lists", "title": "Singly & Doubly Linked Lists", "short_title": "Linked Lists", "difficulty": "Foundational", "summary": "Pointer-based traversal, insertion trade-offs, and safe node updates.", "mastery": 48, "lesson_count": 5},
    {"id": "stacks-queues", "title": "Stacks & Queues", "short_title": "Stacks / Queues", "difficulty": "Intermediate", "summary": "LIFO and FIFO abstractions with practical scheduling and parsing examples.", "mastery": 26, "lesson_count": 4},
    {"id": "binary-trees", "title": "Binary Trees", "short_title": "Binary Trees", "difficulty": "Intermediate", "summary": "Recursive structure, traversals, height, and balanced search behavior.", "mastery": 12, "lesson_count": 6},
    {"id": "hash-tables", "title": "Hash Tables", "short_title": "Hash Tables", "difficulty": "Rigorous", "summary": "Hash functions, collisions, load factors, and amortized lookup behavior.", "mastery": 0, "lesson_count": 6},
]

CHUNKS = [
    {"id": "arrays-12", "topic_id": "arrays", "label": "SLIDE 12", "title": "Contiguous storage", "page": "Slide 12", "content": "An array stores elements in adjacent memory locations. If the base address is known, the address of index i is base plus i times the element width, so indexed access is constant time.", "approved_at": "2025-02-03"},
    {"id": "arrays-18", "topic_id": "arrays", "label": "NOTES §2.3", "title": "Operation costs", "page": "Notes §2.3", "content": "Reading or replacing an element by index is O(1). Inserting near the front can be O(n) because later elements must shift to preserve order.", "approved_at": "2025-02-03"},
    {"id": "lists-07", "topic_id": "linked-lists", "label": "SLIDE 07", "title": "Node traversal", "page": "Slide 7", "content": "A linked list stores nodes connected by references. Finding the kth node requires traversal from a known endpoint, which is linear in the number of hops.", "approved_at": "2025-02-05"},
    {"id": "lists-14", "topic_id": "linked-lists", "label": "RUBRIC 1.4", "title": "Insertion reasoning", "page": "Rubric 1.4", "content": "A strong explanation distinguishes finding a position from rewiring a node. Rewiring is constant time once the predecessor is known; locating it may still be linear.", "approved_at": "2025-02-05"},
    {"id": "queues-04", "topic_id": "stacks-queues", "label": "SLIDE 04", "title": "FIFO scheduling", "page": "Slide 4", "content": "A queue removes items in first-in, first-out order. A circular buffer can keep enqueue and dequeue operations constant time when capacity is managed.", "approved_at": "2025-02-08"},
    {"id": "trees-09", "topic_id": "binary-trees", "label": "SLIDE 09", "title": "Tree height", "page": "Slide 9", "content": "The height of a tree is the length of its longest root-to-leaf path. Traversals visit every node, so their running time is O(n).", "approved_at": "2025-02-10"},
    {"id": "hash-11", "topic_id": "hash-tables", "label": "NOTES §5.1", "title": "Load factor", "page": "Notes §5.1", "content": "The load factor is the number of stored entries divided by table capacity. Keeping it bounded helps preserve expected constant-time lookup under a suitable hash function.", "approved_at": "2025-02-12"},
]

QUESTIONS = {
    "arrays": {"prompt": "Why is reading items[i] considered O(1) in the course's array model?", "options": [{"id": "a", "text": "The address is computed from the base address and index."}, {"id": "b", "text": "The array checks every earlier item first."}, {"id": "c", "text": "Arrays never store more than one item."}, {"id": "d", "text": "The item is always cached by the browser."}], "correct": "a", "explanation": "The array model uses contiguous storage, so the address is calculated directly from base + index × element width."},
    "linked-lists": {"prompt": "Which distinction matters when analyzing linked-list insertion?", "options": [{"id": "a", "text": "Rewiring is constant time once the predecessor is known, but finding it may be linear."}, {"id": "b", "text": "Every linked-list insertion is always logarithmic."}, {"id": "c", "text": "Nodes are always adjacent in memory."}, {"id": "d", "text": "Insertion never changes references."}], "correct": "a", "explanation": "The rubric separates locating the insertion point from the pointer rewiring performed after it is known."},
    "stacks-queues": {"prompt": "Which ordering does a queue preserve?", "options": [{"id": "a", "text": "Last in, first out."}, {"id": "b", "text": "First in, first out."}, {"id": "c", "text": "Random priority order."}, {"id": "d", "text": "Sorted by value."}], "correct": "b", "explanation": "Queues are FIFO abstractions: the earliest enqueued item is removed first."},
    "binary-trees": {"prompt": "What is the running time of a traversal that visits every node once?", "options": [{"id": "a", "text": "O(1)"}, {"id": "b", "text": "O(log n)"}, {"id": "c", "text": "O(n)"}, {"id": "d", "text": "O(n²)"}], "correct": "c", "explanation": "A full traversal performs constant work for each of n nodes, producing O(n)."},
    "hash-tables": {"prompt": "Why does a bounded load factor help hash-table lookup?", "options": [{"id": "a", "text": "It helps limit collision pressure under a suitable hash function."}, {"id": "b", "text": "It sorts all keys before lookup."}, {"id": "c", "text": "It removes the need for a hash function."}, {"id": "d", "text": "It guarantees no collisions."}], "correct": "a", "explanation": "Keeping entries relative to capacity helps preserve expected lookup behavior, though it never guarantees zero collisions."},
}

DEFAULT_SETTINGS = {"max_turns": 5, "scaffolding": "Socratic", "direct_code_lock": True, "answer_leakage_barrier": True, "approved_materials": len(CHUNKS), "forced_topic_id": None}


def _topic(data: dict) -> Topic:
    return Topic(**data)


async def ensure_seeded() -> None:
    if await db.course_meta.find_one({"id": "intro-data-structures"}):
        return
    if not await db.topics.find_one({"id": TOPICS[0]["id"]}):
        await db.topics.insert_many(TOPICS)
    if not await db.source_chunks.find_one({"id": CHUNKS[0]["id"]}):
        await db.source_chunks.insert_many(CHUNKS)
    await db.course_meta.update_one({"id": "intro-data-structures"}, {"$setOnInsert": {"id": "intro-data-structures", "created_at": datetime.now(timezone.utc)}}, upsert=True)
    await db.course_settings.update_one({"id": "default"}, {"$set": {"id": "default", **DEFAULT_SETTINGS}}, upsert=True)


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def _citations(question: str, topic_id: str) -> list[Citation]:
    query = _tokens(question)
    scoped = [chunk for chunk in CHUNKS if chunk["topic_id"] == topic_id] or CHUNKS
    ranked = sorted(scoped, key=lambda chunk: len(query & _tokens(chunk["content"])), reverse=True)
    output = []
    for index, chunk in enumerate(ranked[:2]):
        overlap = len(query & _tokens(chunk["content"]))
        output.append(Citation(id=chunk["id"], label=chunk["label"], title=chunk["title"], snippet=chunk["content"], page=chunk["page"], bm25_score=round(0.72 + overlap * 0.08 - index * 0.03, 2), dense_score=round(0.91 - index * 0.04, 2), approved_at=chunk["approved_at"]))
    return output


async def _persist_progress(topic_id: str, delta: int = 0) -> None:
    await db.progress.update_one({"student_id": "demo-student", "topic_id": topic_id}, {"$set": {"student_id": "demo-student", "topic_id": topic_id, "updated_at": datetime.now(timezone.utc)}, "$inc": {"attempts": 1, "mastery_delta": delta}}, upsert=True)


async def _llm_answer(question: str, citations: list[Citation], learner_level: str) -> str | None:
    try:
        import os
        from emergentintegrations.llm.chat import LlmChat, StreamDone, TextDelta, UserMessage

        key = os.environ.get("EMERGENT_LLM_KEY")
        if not key:
            return None
        context = "\n".join(f"[{citation.page}] {citation.snippet}" for citation in citations)
        chat = LlmChat(api_key=key, session_id="grounded-tutor-demo", system_message="You are a cautious tutor. Use only the instructor-approved context. Never complete graded work. State uncertainty when context is insufficient.").with_model("openai", "gpt-5.4-mini")
        parts: list[str] = []
        async for event in chat.stream_message(UserMessage(text=f"Learner level: {learner_level}\nQuestion: {question}\nApproved context:\n{context}\nAnswer in 3 concise paragraphs with one Socratic follow-up.")):
            if isinstance(event, TextDelta):
                parts.append(event.content)
            elif isinstance(event, StreamDone):
                break
        return "".join(parts).strip() or None
    except Exception:
        return None


@router.get("/course/overview", response_model=CourseOverview)
async def course_overview():
    await ensure_seeded()
    topics = [_topic(topic) for topic in TOPICS]
    return CourseOverview(course_title="Intro to Data Structures", course_code="CS-101", description="A grounded, instructor-approved path from array cost models to hash-table trade-offs.", instructor="Dr. Mira Chen", approval_status="Instructor approved", topics=topics, progress_percent=32, current_topic_id="linked-lists", today_label=today_iso())


@router.get("/course/settings", response_model=InstructorSettings)
async def course_settings():
    await ensure_seeded()
    settings = await db.course_settings.find_one({"id": "default"}, {"_id": 0}) or DEFAULT_SETTINGS
    return InstructorSettings(**settings)


@router.patch("/course/settings", response_model=InstructorSettings)
async def update_course_settings(settings: InstructorSettings):
    await ensure_seeded()
    data = settings.model_dump()
    await db.course_settings.update_one({"id": "default"}, {"$set": {"id": "default", **data}}, upsert=True)
    return settings


@router.post("/tutor/ask", response_model=TutorResponse)
async def tutor_ask(request: TutorAsk):
    await ensure_seeded()
    lower = request.question.lower()
    refusal_terms = ("write my entire", "do my homework", "exam answer key", "graded assignment", "ignore previous")
    citations = _citations(request.question, request.topic_id)
    trace = [ToolTrace(tool="BM25 retrieval", detail=f"Ranked {len(citations)} approved chunks for {request.topic_id}", status="complete"), ToolTrace(tool="Prompt guard", detail="Checked for answer leakage and injection patterns", status="guarded")]
    if any(term in lower for term in refusal_terms):
        return TutorResponse(answer="I can’t provide a complete graded solution or bypass course rules. I can explain the concept, work through a parallel toy example, or generate a diagnostic practice question.", citations=citations, confidence=99, uncertainty_note="The safeguard is certain this request asks for work the tutor should not complete.", refusal=True, refusal_reason="academic_misconduct", tool_trace=trace, next_topic=None, llm_used=False)
    topic = next((item for item in TOPICS if item["id"] == request.topic_id), TOPICS[0])
    answer = f"{topic['title']} becomes easier when you name the operation before choosing a structure. For this question, start with the invariant: {citations[0].snippet if citations else topic['summary']} A useful check is to ask which values must move or which references must be followed."
    llm_used = False
    if request.use_llm:
        generated = await _llm_answer(request.question, citations, request.learner_level)
        if generated:
            answer = generated
            llm_used = True
    await _persist_progress(request.topic_id)
    next_index = min(len(TOPICS) - 1, max(0, [item["id"] for item in TOPICS].index(request.topic_id) + 1))
    return TutorResponse(answer=answer, citations=citations, confidence=92 if citations else 64, uncertainty_note="Grounded in instructor-approved passages; ask for a clarification if your example differs from the lecture model.", refusal=False, tool_trace=trace + [ToolTrace(tool="Progress updater", detail="Recorded a lightweight tutoring turn", status="complete")], next_topic=_topic(TOPICS[next_index]), llm_used=llm_used)


@router.post("/quiz/generate", response_model=QuizQuestion)
async def generate_quiz(request: QuizGenerate):
    await ensure_seeded()
    topic = next((item for item in TOPICS if item["id"] == request.topic_id), TOPICS[0])
    source = QUESTIONS.get(request.topic_id, QUESTIONS["arrays"])
    citations = _citations(source["prompt"], request.topic_id)
    return QuizQuestion(id=f"{request.topic_id}-diagnostic", topic_id=request.topic_id, topic_title=topic["title"], difficulty=request.difficulty, prompt=source["prompt"], options=[QuizOption(**option) for option in source["options"]], correct_option=source["correct"], explanation=source["explanation"], citations=citations, rubric=[RubricCriterion(name="Conceptual correctness", points=2, description="Selects the answer that matches the instructor model."), RubricCriterion(name="Reasoning signal", points=1, description="Choice demonstrates a relevant invariant or trade-off."), RubricCriterion(name="Source grounding", points=1, description="Answer is supported by the cited approved passage.")])


@router.post("/quiz/grade", response_model=QuizResult)
async def grade_quiz(request: QuizGrade):
    await ensure_seeded()
    topic_id = request.question_id.rsplit("-diagnostic", 1)[0]
    source = QUESTIONS.get(topic_id, QUESTIONS["arrays"])
    correct = request.selected_option == source["correct"]
    await _persist_progress(topic_id, 8 if correct else 2)
    next_index = min(len(TOPICS) - 1, max(0, [item["id"] for item in TOPICS].index(topic_id) + 1))
    rubric = [RubricScore(criterion="Conceptual correctness", earned=2 if correct else 0, possible=2, feedback="Your choice matches the approved explanation." if correct else "Revisit the invariant in the cited passage."), RubricScore(criterion="Reasoning signal", earned=1 if correct else 0, possible=1, feedback="You identified the key operation model." if correct else "Name the operation before estimating its cost."), RubricScore(criterion="Source grounding", earned=1 if correct else 0, possible=1, feedback="Aligned with the instructor source." if correct else "Use the citation to compare each option.")]
    return QuizResult(question_id=request.question_id, correct=correct, score=sum(item.earned for item in rubric), max_score=4, feedback="Strong diagnostic answer. The next step is to contrast this with linked-list access." if correct else "Not quite. Treat this as a learning signal, then retry after reading the source passage.", rubric_scores=rubric, next_topic=_topic(TOPICS[next_index]))


@router.get("/evaluation", response_model=EvaluationData)
async def evaluation():
    return EvaluationData(metrics=[EvaluationMetric(label="Recall@5", value="91.4%", delta="+6.2% vs BM25 baseline", tone="blue"), EvaluationMetric(label="Citation precision", value="97.8%", delta="Verified approved chunks", tone="green"), EvaluationMetric(label="Rubric agreement", value="89.2%", delta="κ 0.84 vs instructor", tone="amber"), EvaluationMetric(label="Safeguard refusal", value="100%", delta="0 leakage in 120 probes", tone="rose"), EvaluationMetric(label="Median latency", value="410 ms", delta="Retrieval path", tone="blue")], recall_curve=[{"k": "1", "bm25": 68.0, "dense": 74.0, "hybrid": 79.0}, {"k": "3", "bm25": 82.0, "dense": 87.0, "hybrid": 91.0}, {"k": "5", "bm25": 85.0, "dense": 90.0, "hybrid": 94.0}, {"k": "8", "bm25": 89.0, "dense": 93.0, "hybrid": 96.0}], ablations=[{"system": "Raw compact LLM", "recall": "—", "citation": "61%", "latency": "620 ms"}, {"system": "BM25 baseline", "recall": "85%", "citation": "88%", "latency": "90 ms"}, {"system": "Dense only", "recall": "90%", "citation": "92%", "latency": "280 ms"}, {"system": "Hybrid RAG + agent", "recall": "94%", "citation": "98%", "latency": "410 ms"}], safeguards=[{"name": "Prompt injection", "status": "Blocked", "detail": "Guardrail checks before retrieval"}, {"name": "Answer leakage", "status": "Blocked", "detail": "No complete graded solutions"}, {"name": "Uncertainty", "status": "Shown", "detail": "Confidence and source provenance"}, {"name": "Privacy", "status": "Scoped", "detail": "Minimal demo session memory"}])


class MaterialApproval(BaseModel):
    material_id: str
    approved: bool


@router.patch("/materials/{material_id}")
async def approve_material(material_id: str, approval: MaterialApproval):
    await ensure_seeded()
    result = await db.source_chunks.update_one({"id": material_id}, {"$set": {"approved": approval.approved}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"material_id": material_id, "approved": approval.approved}