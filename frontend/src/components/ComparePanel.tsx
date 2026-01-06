import { AIModel } from '@/data/models';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';
import { X, ArrowLeftRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ComparePanelProps {
  models: AIModel[];
  onRemove: (id: string) => void;
  onClear: () => void;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ComparePanel({ models, onRemove, onClear, isOpen, onOpenChange }: ComparePanelProps) {
  const allBenchmarks = [...new Set(models.flatMap(m => m.benchmarks.map(b => b.name)))];

  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="h-[80vh] bg-card border-border">
        <SheetHeader className="pb-4 border-b border-border">
          <div className="flex items-center justify-between">
            <SheetTitle className="flex items-center gap-2 text-2xl">
              <ArrowLeftRight className="h-6 w-6 text-primary" />
              Compare Models ({models.length})
            </SheetTitle>
            <Button variant="ghost" size="sm" onClick={onClear}>
              Clear all
            </Button>
          </div>
        </SheetHeader>

        <div className="mt-6 overflow-x-auto">
          <div className="inline-flex gap-6 min-w-full pb-4">
            {models.map((model) => (
              <div 
                key={model.id}
                className="flex-shrink-0 w-80 p-6 rounded-xl bg-secondary/30 border border-border/50 relative"
              >
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-2 right-2 h-8 w-8"
                  onClick={() => onRemove(model.id)}
                >
                  <X className="h-4 w-4" />
                </Button>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-xl font-semibold">{model.name}</h3>
                    <p className="text-sm text-muted-foreground">{model.provider}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-3 py-4 border-y border-border/50">
                    <div>
                      <p className="text-xs text-muted-foreground">Parameters</p>
                      <p className="font-mono font-medium">{model.parameters}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Context</p>
                      <p className="font-mono font-medium">{model.contextWindow}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Input Price</p>
                      <p className="font-mono font-medium text-sm">{model.pricing.input}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Output Price</p>
                      <p className="font-mono font-medium text-sm">{model.pricing.output}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-sm font-medium text-muted-foreground">Benchmarks</h4>
                    {allBenchmarks.map((benchName) => {
                      const bench = model.benchmarks.find(b => b.name === benchName);
                      const score = bench?.score ?? 0;
                      const maxScore = bench?.maxScore ?? 100;
                      const isTop = models.every(m => {
                        const other = m.benchmarks.find(b => b.name === benchName);
                        return !other || score >= other.score;
                      });

                      return (
                        <div key={benchName} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">{benchName}</span>
                            <span className={cn(
                              "font-mono font-medium",
                              isTop && score > 0 && "text-primary"
                            )}>
                              {score > 0 ? `${score}%` : 'N/A'}
                            </span>
                          </div>
                          <Progress 
                            value={(score / maxScore) * 100} 
                            className={cn("h-1.5", isTop && score > 0 && "[&>div]:bg-primary")}
                          />
                        </div>
                      );
                    })}
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {model.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="tag" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
