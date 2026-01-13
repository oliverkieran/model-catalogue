import { AIModel } from "@/types/api";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Code,
  Pencil,
  Image,
  FileText,
  BookOpen,
  Shield,
  Video,
  FolderCode,
  Layers,
  Server,
  Settings,
  Lock,
  Globe,
  CheckCircle,
  Mic,
  Languages,
  Captions,
  Palette,
  Box,
  Brain,
  FlaskConical,
  Cpu,
  Star,
  Calendar,
  DollarSign,
  Zap,
  ArrowUpRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const iconMap: Record<string, React.ReactNode> = {
  code: <Code className="h-5 w-5" />,
  pencil: <Pencil className="h-5 w-5" />,
  image: <Image className="h-5 w-5" />,
  "file-text": <FileText className="h-5 w-5" />,
  "book-open": <BookOpen className="h-5 w-5" />,
  shield: <Shield className="h-5 w-5" />,
  video: <Video className="h-5 w-5" />,
  "folder-code": <FolderCode className="h-5 w-5" />,
  layers: <Layers className="h-5 w-5" />,
  server: <Server className="h-5 w-5" />,
  settings: <Settings className="h-5 w-5" />,
  lock: <Lock className="h-5 w-5" />,
  globe: <Globe className="h-5 w-5" />,
  "check-circle": <CheckCircle className="h-5 w-5" />,
  mic: <Mic className="h-5 w-5" />,
  languages: <Languages className="h-5 w-5" />,
  captions: <Captions className="h-5 w-5" />,
  palette: <Palette className="h-5 w-5" />,
  box: <Box className="h-5 w-5" />,
  brain: <Brain className="h-5 w-5" />,
  flask: <FlaskConical className="h-5 w-5" />,
  cpu: <Cpu className="h-5 w-5" />,
};

interface ModelDetailProps {
  model: AIModel | null;
  onClose: () => void;
}

export function ModelDetail({ model, onClose }: ModelDetailProps) {
  if (!model) return null;

  //const typeInfo = modelTypes.find((t) => t.value === model.type);
  const avgRating = 4.66; // HARDCODED FOR NOW, REPLACE WITH CALCULATION BASED ON model.opinions WHEN AVAILABLE

  return (
    <Dialog open={!!model} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-card border-border">
        <DialogHeader className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <DialogTitle className="text-3xl font-bold">
                  {model.display_name}
                </DialogTitle>
                {/* <Badge variant={model.type} className="text-sm">
                  {typeInfo?.label}
                </Badge> */}
              </div>
              <p className="text-lg text-muted-foreground">{model.name}</p>
            </div>
            <div className="text-right space-y-1">
              <div className="flex items-center gap-1 text-model-multimodal">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={cn(
                      "h-5 w-5",
                      i < Math.round(avgRating)
                        ? "fill-current"
                        : "fill-none opacity-30"
                    )}
                  />
                ))}
              </div>
              <p className="text-sm text-muted-foreground">
                3 reviews
                {/* {model.opinions.length} reviews */}
              </p>
            </div>
          </div>
          <p className="text-muted-foreground">{model.description}</p>
        </DialogHeader>

        {/* <div className="grid grid-cols-4 gap-4 py-6 border-y border-border">
          <div className="text-center p-4 rounded-lg bg-secondary/30">
            <Zap className="h-5 w-5 mx-auto mb-2 text-primary" />
            <p className="text-xs text-muted-foreground mb-1">Parameters</p>
            <p className="font-mono font-semibold">{model.parameters}</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-secondary/30">
            <FileText className="h-5 w-5 mx-auto mb-2 text-model-vision" />
            <p className="text-xs text-muted-foreground mb-1">Context Window</p>
            <p className="font-mono font-semibold">{model.contextWindow}</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-secondary/30">
            <Calendar className="h-5 w-5 mx-auto mb-2 text-model-audio" />
            <p className="text-xs text-muted-foreground mb-1">Released</p>
            <p className="font-mono font-semibold">{model.releaseDate}</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-secondary/30">
            <DollarSign className="h-5 w-5 mx-auto mb-2 text-model-multimodal" />
            <p className="text-xs text-muted-foreground mb-1">Pricing</p>
            <p className="font-mono font-semibold text-sm">
              {model.pricing.input}
            </p>
          </div>
        </div> */}

        <Tabs defaultValue="benchmarks" className="mt-6">
          <TabsList className="w-full justify-start bg-secondary/30 p-1">
            <TabsTrigger value="benchmarks" className="flex-1">
              Benchmarks
            </TabsTrigger>
            <TabsTrigger value="usecases" className="flex-1">
              Use Cases
            </TabsTrigger>
            <TabsTrigger value="opinions" className="flex-1">
              Opinions
            </TabsTrigger>
          </TabsList>

          <TabsContent value="benchmarks" className="mt-6 space-y-4">
            {[
              {
                name: "MMLU",
                category: "Knowledge",
                score: 92,
                maxScore: 100,
              },
              {
                name: "HumanEval",
                category: "Coding",
                score: 88,
                maxScore: 100,
              },
              {
                name: "GSM8K",
                category: "Math",
                score: 85,
                maxScore: 100,
              },
              {
                name: "BLEU",
                category: "Translation",
                score: 38,
                maxScore: 50,
              },
              {
                name: "TruthfulQA",
                category: "Truthfulness",
                score: 82,
                maxScore: 100,
              },
            ].map((benchmark) => (
              <div key={benchmark.name} className="space-y-2">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{benchmark.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {benchmark.category}
                    </Badge>
                  </div>
                  <span className="font-mono font-semibold text-primary">
                    {benchmark.score}/{benchmark.maxScore}
                  </span>
                </div>
                <Progress
                  value={(benchmark.score / benchmark.maxScore) * 100}
                  className="h-2"
                />
              </div>
            ))}
          </TabsContent>

          <TabsContent value="usecases" className="mt-6">
            <div className="grid gap-4 md:grid-cols-3">
              {[
                {
                  title: "Content Generation",
                  description:
                    "Create high-quality text, articles, and creative content",
                  icon: "pencil",
                },
                {
                  title: "Code Assistance",
                  description:
                    "Generate, debug, and optimize code across multiple languages",
                  icon: "code",
                },
                {
                  title: "Data Analysis",
                  description:
                    "Analyze datasets and extract meaningful insights",
                  icon: "layers",
                },
                {
                  title: "Image Generation",
                  description:
                    "Create and manipulate images from text descriptions",
                  icon: "image",
                },
                {
                  title: "Research Support",
                  description:
                    "Assist with literature review and research documentation",
                  icon: "book-open",
                },
                {
                  title: "Customer Support",
                  description:
                    "Provide intelligent responses to customer inquiries",
                  icon: "shield",
                },
              ].map((useCase) => (
                <div
                  key={useCase.title}
                  className="p-5 rounded-xl bg-secondary/30 border border-border/50 hover:border-primary/50 transition-colors group"
                >
                  <div className="p-3 rounded-lg bg-primary/10 text-primary w-fit mb-4 group-hover:scale-110 transition-transform">
                    {iconMap[useCase.icon] || <Code className="h-5 w-5" />}
                  </div>
                  <h4 className="font-semibold mb-2">{useCase.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {useCase.description}
                  </p>
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="opinions" className="mt-6 space-y-4">
            {[
              {
                author: "Sarah Chen",
                role: "ML Engineer",
                rating: 5,
                content:
                  "Exceptional performance on our benchmark tests. The model consistently outperforms competitors.",
              },
              {
                author: "James Mitchell",
                role: "Product Manager",
                rating: 4,
                content:
                  "Great capabilities but API latency could be improved for real-time applications.",
              },
              {
                author: "Dr. Amelia Rodriguez",
                role: "Research Scientist",
                rating: 5,
                content:
                  "Impressive accuracy and the documentation is thorough. Highly recommended for production use.",
              },
            ].map((opinion, idx) => (
              <div
                key={idx}
                className="p-5 rounded-xl bg-secondary/30 border border-border/50"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold">{opinion.author}</p>
                    <p className="text-sm text-muted-foreground">
                      {opinion.role}
                    </p>
                  </div>
                  <div className="flex items-center gap-0.5 text-model-multimodal">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={cn(
                          "h-4 w-4",
                          i < opinion.rating
                            ? "fill-current"
                            : "fill-none opacity-30"
                        )}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-muted-foreground italic">
                  "{opinion.content}"
                </p>
              </div>
            ))}
          </TabsContent>
        </Tabs>

        {/* <div className="flex flex-wrap gap-2 mt-6 pt-6 border-t border-border">
          {model.tags.map((tag) => (
            <Badge key={tag} variant="tag">
              {tag}
            </Badge>
          ))}
        </div> */}

        <div className="flex justify-end mt-6">
          <Button variant="hero" className="gap-2">
            Visit Organization
            <ArrowUpRight className="h-4 w-4" />
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
