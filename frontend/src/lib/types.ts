export interface Topic {
  id: string;
  title: string;
  short_title: string;
  difficulty: "Foundational" | "Intermediate" | "Rigorous";
  summary: string;
  mastery: number;
  lesson_count: number;
}

export interface Citation {
  id: string;
  label: string;
  title: string;
  snippet: string;
  page: string;
  bm25_score: number;
  dense_score: number;
  approved_at: string;
}

export interface CourseOverview {
  course_title: string;
  course_code: string;
  description: string;
  instructor: string;
  approval_status: string;
  topics: Topic[];
  progress_percent: number;
  current_topic_id: string;
  today_label: string;
}

export interface ToolTrace {
  tool: string;
  detail: string;
  status: "complete" | "guarded";
}

export interface TutorResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  uncertainty_note: string;
  refusal: boolean;
  refusal_reason?: string | null;
  tool_trace: ToolTrace[];
  next_topic?: Topic | null;
  llm_used: boolean;
}

export interface TutorAskRequest {
  question: string;
  topic_id: string;
  learner_level: "Foundational" | "Intermediate" | "Rigorous";
  use_llm: boolean;
}

export interface QuizOption {
  id: string;
  text: string;
}

export interface RubricCriterion {
  name: string;
  points: number;
  description: string;
}

export interface QuizQuestion {
  id: string;
  topic_id: string;
  topic_title: string;
  difficulty: string;
  prompt: string;
  options: QuizOption[];
  correct_option: string;
  explanation: string;
  citations: Citation[];
  rubric: RubricCriterion[];
}

export interface QuizGenerateRequest {
  topic_id: string;
  difficulty: "Foundational" | "Intermediate" | "Rigorous";
}

export interface QuizGradeRequest {
  question_id: string;
  selected_option: string;
}

export interface RubricScore {
  criterion: string;
  earned: number;
  possible: number;
  feedback: string;
}

export interface QuizResult {
  question_id: string;
  correct: boolean;
  score: number;
  max_score: number;
  feedback: string;
  rubric_scores: RubricScore[];
  next_topic?: Topic | null;
}

export interface InstructorSettings {
  max_turns: number;
  scaffolding: "Socratic" | "Balanced" | "Direct";
  direct_code_lock: boolean;
  answer_leakage_barrier: boolean;
  approved_materials: number;
  forced_topic_id?: string | null;
}

export interface EvaluationMetric {
  label: string;
  value: string;
  delta: string;
  tone: "blue" | "green" | "amber" | "rose";
}

export interface EvaluationData {
  metrics: EvaluationMetric[];
  recall_curve: Array<{ k: string; bm25: number; dense: number; hybrid: number }>;
  ablations: Array<{ system: string; recall: string; citation: string; latency: string }>;
  safeguards: Array<{ name: string; status: string; detail: string }>;
}

export interface MaterialApproval {
  material_id: string;
  approved: boolean;
}

export interface MaterialApprovalResponse {
  material_id: string;
  approved: boolean;
}

export const fallbackTopics: Topic[] = [
  { id: "arrays", title: "Arrays & Complexity", short_title: "Arrays", difficulty: "Foundational", summary: "Indexing, contiguous memory, and operation cost.", mastery: 72, lesson_count: 4 },
  { id: "linked-lists", title: "Singly & Doubly Linked Lists", short_title: "Linked Lists", difficulty: "Foundational", summary: "Traversal, insertion, and safe pointer updates.", mastery: 48, lesson_count: 5 },
  { id: "stacks-queues", title: "Stacks & Queues", short_title: "Stacks / Queues", difficulty: "Intermediate", summary: "LIFO and FIFO abstractions.", mastery: 26, lesson_count: 4 },
  { id: "binary-trees", title: "Binary Trees", short_title: "Binary Trees", difficulty: "Intermediate", summary: "Traversal, height, and recursive structure.", mastery: 12, lesson_count: 6 },
  { id: "hash-tables", title: "Hash Tables", short_title: "Hash Tables", difficulty: "Rigorous", summary: "Collisions, load factors, and lookup trade-offs.", mastery: 0, lesson_count: 6 },
];