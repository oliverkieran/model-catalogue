export type ModelType = 'language' | 'vision' | 'audio' | 'multimodal';

export interface Benchmark {
  name: string;
  score: number;
  maxScore: number;
  category: string;
}

export interface UseCase {
  title: string;
  description: string;
  icon: string;
}

export interface Opinion {
  author: string;
  role: string;
  content: string;
  rating: number;
  avatar?: string;
}

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  type: ModelType;
  description: string;
  releaseDate: string;
  parameters: string;
  contextWindow: string;
  pricing: {
    input: string;
    output: string;
  };
  benchmarks: Benchmark[];
  useCases: UseCase[];
  opinions: Opinion[];
  tags: string[];
  featured?: boolean;
}

export const models: AIModel[] = [
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'OpenAI',
    type: 'multimodal',
    description: 'OpenAI\'s most advanced multimodal model, capable of processing text, images, and audio with human-level performance on various benchmarks.',
    releaseDate: '2024-05',
    parameters: '~1.8T',
    contextWindow: '128K',
    pricing: { input: '$5.00/1M', output: '$15.00/1M' },
    benchmarks: [
      { name: 'MMLU', score: 88.7, maxScore: 100, category: 'Knowledge' },
      { name: 'HumanEval', score: 90.2, maxScore: 100, category: 'Coding' },
      { name: 'MATH', score: 76.6, maxScore: 100, category: 'Reasoning' },
      { name: 'GPQA', score: 53.6, maxScore: 100, category: 'Science' },
    ],
    useCases: [
      { title: 'Code Generation', description: 'Write, debug, and explain complex code across languages', icon: 'code' },
      { title: 'Content Creation', description: 'Generate high-quality articles, stories, and marketing copy', icon: 'pencil' },
      { title: 'Image Analysis', description: 'Analyze and describe images with remarkable accuracy', icon: 'image' },
    ],
    opinions: [
      { author: 'Sarah Chen', role: 'ML Engineer at Meta', content: 'The multimodal capabilities are game-changing. Finally a model that understands context across modalities.', rating: 5 },
      { author: 'James Wilson', role: 'Tech Lead at Stripe', content: 'Excellent for production use. The API is stable and the results are consistent.', rating: 4 },
    ],
    tags: ['multimodal', 'vision', 'coding', 'reasoning'],
    featured: true,
  },
  {
    id: 'claude-4-sonnet',
    name: 'Claude 4 Sonnet',
    provider: 'Anthropic',
    type: 'language',
    description: 'Anthropic\'s balanced model offering excellent performance with improved safety features and nuanced understanding of complex instructions.',
    releaseDate: '2025-05',
    parameters: 'Unknown',
    contextWindow: '200K',
    pricing: { input: '$3.00/1M', output: '$15.00/1M' },
    benchmarks: [
      { name: 'MMLU', score: 89.0, maxScore: 100, category: 'Knowledge' },
      { name: 'HumanEval', score: 92.0, maxScore: 100, category: 'Coding' },
      { name: 'MATH', score: 78.3, maxScore: 100, category: 'Reasoning' },
      { name: 'GPQA', score: 59.4, maxScore: 100, category: 'Science' },
    ],
    useCases: [
      { title: 'Long Documents', description: 'Process and analyze documents up to 200K tokens', icon: 'file-text' },
      { title: 'Research Assistant', description: 'Help with academic research and literature review', icon: 'book-open' },
      { title: 'Code Review', description: 'Thorough code review with security focus', icon: 'shield' },
    ],
    opinions: [
      { author: 'Emily Zhang', role: 'AI Researcher at Stanford', content: 'Best-in-class for nuanced reasoning tasks. The extended context window is invaluable.', rating: 5 },
      { author: 'Michael Park', role: 'CTO at Notion', content: 'We use Claude for our AI features. Great balance of capability and safety.', rating: 5 },
    ],
    tags: ['long-context', 'reasoning', 'coding', 'safe'],
    featured: true,
  },
  {
    id: 'gemini-2.5-pro',
    name: 'Gemini 2.5 Pro',
    provider: 'Google',
    type: 'multimodal',
    description: 'Google\'s flagship multimodal model with native image, video, and audio understanding plus exceptional coding abilities.',
    releaseDate: '2025-03',
    parameters: 'Unknown',
    contextWindow: '1M',
    pricing: { input: '$1.25/1M', output: '$5.00/1M' },
    benchmarks: [
      { name: 'MMLU', score: 90.2, maxScore: 100, category: 'Knowledge' },
      { name: 'HumanEval', score: 89.5, maxScore: 100, category: 'Coding' },
      { name: 'MATH', score: 80.1, maxScore: 100, category: 'Reasoning' },
      { name: 'GPQA', score: 62.0, maxScore: 100, category: 'Science' },
    ],
    useCases: [
      { title: 'Video Analysis', description: 'Understand and analyze video content natively', icon: 'video' },
      { title: 'Codebase Understanding', description: 'Process entire codebases with 1M context', icon: 'folder-code' },
      { title: 'Multimodal RAG', description: 'Build apps that understand text, images, and more', icon: 'layers' },
    ],
    opinions: [
      { author: 'David Kim', role: 'Principal Engineer at Vercel', content: 'The 1M context window changes everything for code understanding tasks.', rating: 5 },
      { author: 'Lisa Wang', role: 'AI Lead at Spotify', content: 'Great for multimodal applications, especially with audio content.', rating: 4 },
    ],
    tags: ['multimodal', 'video', 'long-context', 'coding'],
    featured: true,
  },
  {
    id: 'llama-3.3-70b',
    name: 'Llama 3.3 70B',
    provider: 'Meta',
    type: 'language',
    description: 'Meta\'s open-source powerhouse delivering near-frontier performance with full weight availability for customization.',
    releaseDate: '2024-12',
    parameters: '70B',
    contextWindow: '128K',
    pricing: { input: 'Free (OSS)', output: 'Free (OSS)' },
    benchmarks: [
      { name: 'MMLU', score: 86.0, maxScore: 100, category: 'Knowledge' },
      { name: 'HumanEval', score: 88.4, maxScore: 100, category: 'Coding' },
      { name: 'MATH', score: 77.0, maxScore: 100, category: 'Reasoning' },
      { name: 'GPQA', score: 50.0, maxScore: 100, category: 'Science' },
    ],
    useCases: [
      { title: 'Self-Hosting', description: 'Run on your own infrastructure with full control', icon: 'server' },
      { title: 'Fine-Tuning', description: 'Customize for your specific use case', icon: 'settings' },
      { title: 'Privacy-First Apps', description: 'Keep all data on-premise', icon: 'lock' },
    ],
    opinions: [
      { author: 'Alex Thompson', role: 'Open Source Lead at HuggingFace', content: 'The best open-source model available. Incredible value for fine-tuning.', rating: 5 },
      { author: 'Rachel Green', role: 'ML Engineer at Shopify', content: 'We fine-tuned it for our use case and results match GPT-4 for our domain.', rating: 4 },
    ],
    tags: ['open-source', 'fine-tunable', 'self-hosted'],
  },
  {
    id: 'mistral-large-2',
    name: 'Mistral Large 2',
    provider: 'Mistral AI',
    type: 'language',
    description: 'European AI leader\'s flagship model with strong multilingual capabilities and excellent reasoning performance.',
    releaseDate: '2024-07',
    parameters: '123B',
    contextWindow: '128K',
    pricing: { input: '$2.00/1M', output: '$6.00/1M' },
    benchmarks: [
      { name: 'MMLU', score: 84.0, maxScore: 100, category: 'Knowledge' },
      { name: 'HumanEval', score: 92.0, maxScore: 100, category: 'Coding' },
      { name: 'MATH', score: 76.9, maxScore: 100, category: 'Reasoning' },
      { name: 'GPQA', score: 49.1, maxScore: 100, category: 'Science' },
    ],
    useCases: [
      { title: 'Multilingual Apps', description: 'Excellent performance across 80+ languages', icon: 'globe' },
      { title: 'Code Generation', description: 'Top-tier coding with function calling', icon: 'code' },
      { title: 'EU Compliance', description: 'European company with GDPR compliance', icon: 'check-circle' },
    ],
    opinions: [
      { author: 'Pierre Dubois', role: 'CTO at BlaBlaCar', content: 'Best choice for European companies needing GDPR compliance.', rating: 4 },
      { author: 'Anna Schmidt', role: 'AI Architect at SAP', content: 'Outstanding multilingual performance for our global customer base.', rating: 5 },
    ],
    tags: ['multilingual', 'coding', 'eu-compliant'],
  },
  {
    id: 'whisper-large-v3',
    name: 'Whisper Large V3',
    provider: 'OpenAI',
    type: 'audio',
    description: 'State-of-the-art speech recognition model supporting 100+ languages with excellent accuracy and timestamp generation.',
    releaseDate: '2023-11',
    parameters: '1.5B',
    contextWindow: '30s chunks',
    pricing: { input: '$0.006/min', output: 'N/A' },
    benchmarks: [
      { name: 'WER English', score: 96.1, maxScore: 100, category: 'Accuracy' },
      { name: 'WER Multilingual', score: 89.0, maxScore: 100, category: 'Accuracy' },
      { name: 'Speed', score: 85.0, maxScore: 100, category: 'Performance' },
      { name: 'Noise Robustness', score: 88.0, maxScore: 100, category: 'Robustness' },
    ],
    useCases: [
      { title: 'Transcription', description: 'Convert audio to text with high accuracy', icon: 'mic' },
      { title: 'Translation', description: 'Translate audio directly to English', icon: 'languages' },
      { title: 'Subtitles', description: 'Generate accurate subtitles with timestamps', icon: 'captions' },
    ],
    opinions: [
      { author: 'Tom Harris', role: 'Product Lead at Descript', content: 'Gold standard for transcription. We use it as our primary ASR engine.', rating: 5 },
      { author: 'Maria Garcia', role: 'ML Engineer at Duolingo', content: 'Excellent multilingual support for our language learning platform.', rating: 4 },
    ],
    tags: ['speech', 'transcription', 'multilingual'],
  },
  {
    id: 'stable-diffusion-3',
    name: 'Stable Diffusion 3',
    provider: 'Stability AI',
    type: 'vision',
    description: 'Latest text-to-image model with improved typography, photorealism, and prompt adherence using advanced MMDiT architecture.',
    releaseDate: '2024-06',
    parameters: '8B',
    contextWindow: 'N/A',
    pricing: { input: 'Free (OSS)', output: 'Free (OSS)' },
    benchmarks: [
      { name: 'Prompt Adherence', score: 91.0, maxScore: 100, category: 'Quality' },
      { name: 'Typography', score: 88.0, maxScore: 100, category: 'Quality' },
      { name: 'Photorealism', score: 86.0, maxScore: 100, category: 'Quality' },
      { name: 'Speed', score: 82.0, maxScore: 100, category: 'Performance' },
    ],
    useCases: [
      { title: 'Image Generation', description: 'Create stunning images from text descriptions', icon: 'image' },
      { title: 'Design Assets', description: 'Generate marketing and design materials', icon: 'palette' },
      { title: 'Product Mockups', description: 'Quick visualization of product ideas', icon: 'box' },
    ],
    opinions: [
      { author: 'Chris Lee', role: 'Creative Director at Adobe', content: 'Massive improvement in text rendering. Finally usable for design work.', rating: 4 },
      { author: 'Sophie Martin', role: 'Indie Game Developer', content: 'Perfect for generating game assets. The open-source nature is a huge plus.', rating: 5 },
    ],
    tags: ['image-generation', 'open-source', 'creative'],
  },
  {
    id: 'o3',
    name: 'o3',
    provider: 'OpenAI',
    type: 'language',
    description: 'OpenAI\'s most powerful reasoning model designed for complex problem-solving in mathematics, science, and coding.',
    releaseDate: '2025-04',
    parameters: 'Unknown',
    contextWindow: '200K',
    pricing: { input: '$10.00/1M', output: '$40.00/1M' },
    benchmarks: [
      { name: 'MMLU', score: 91.5, maxScore: 100, category: 'Knowledge' },
      { name: 'HumanEval', score: 96.7, maxScore: 100, category: 'Coding' },
      { name: 'MATH', score: 96.4, maxScore: 100, category: 'Reasoning' },
      { name: 'GPQA', score: 87.7, maxScore: 100, category: 'Science' },
    ],
    useCases: [
      { title: 'Complex Reasoning', description: 'Solve multi-step logical problems', icon: 'brain' },
      { title: 'Scientific Research', description: 'Assist with advanced research tasks', icon: 'flask' },
      { title: 'Algorithm Design', description: 'Design and optimize complex algorithms', icon: 'cpu' },
    ],
    opinions: [
      { author: 'Dr. Amanda Foster', role: 'Research Scientist at DeepMind', content: 'A leap in reasoning capabilities. The chain-of-thought is remarkably coherent.', rating: 5 },
      { author: 'Kevin Wu', role: 'Staff Engineer at Google', content: 'Best for complex coding tasks, but the cost and latency need consideration.', rating: 4 },
    ],
    tags: ['reasoning', 'math', 'science', 'premium'],
    featured: true,
  },
];

export const modelTypes: { value: ModelType; label: string; color: string }[] = [
  { value: 'language', label: 'Language', color: 'model-language' },
  { value: 'vision', label: 'Vision', color: 'model-vision' },
  { value: 'audio', label: 'Audio', color: 'model-audio' },
  { value: 'multimodal', label: 'Multimodal', color: 'model-multimodal' },
];

export const providers = ['OpenAI', 'Anthropic', 'Google', 'Meta', 'Mistral AI', 'Stability AI'];
