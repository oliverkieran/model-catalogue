//import { AIModel, modelTypes } from '@/data/models';
import { AIModel } from "@/types/api";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Sparkles, ArrowRight, Plus, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface ModelCardProps {
  model: AIModel;
  onClick: () => void;
  isComparing: boolean;
  onCompareToggle: () => void;
}

export function ModelCard({
  model,
  onClick,
  isComparing,
  onCompareToggle,
}: ModelCardProps) {
  return (
    <Card
      className={cn(
        "group relative overflow-hidden bg-gradient-card border-border/50 p-6 transition-all duration-300 hover:border-primary/50 hover:shadow-elevated cursor-pointer",
        isComparing && "border-primary ring-2 ring-primary/20"
      )}
    >
      <div onClick={onClick} className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <h3 className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors">
              {model.display_name}
            </h3>
            <p className="text-sm text-muted-foreground">
              {model.organization}
            </p>
          </div>
        </div>

        <p className="text-sm text-muted-foreground line-clamp-2">
          {model.description}
        </p>

        {/* <div className="grid grid-cols-3 gap-3 py-3 border-y border-border/50">
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Parameters</p>
            <p className="text-sm font-medium font-mono">{model.parameters}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Context</p>
            <p className="text-sm font-medium font-mono">
              {model.contextWindow}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Best Score</p>
            <p className="text-sm font-medium font-mono text-primary">
              {topBenchmark.score}%
            </p>
          </div>
        </div> */}

        {/* <div className="flex flex-wrap gap-1.5">
          {model.tags.slice(0, 4).map((tag) => (
            <Badge key={tag} variant="tag" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div> */}
      </div>

      <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/50">
        {/* <Button
          variant="compare"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onCompareToggle();
          }}
          className={cn(isComparing && "bg-primary/20 border-primary")}
        >
          {isComparing ? (
            <Check className="h-4 w-4" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          {isComparing ? "Comparing" : "Compare"}
        </Button> */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onClick}
          className="text-muted-foreground hover:text-primary"
        >
          View details
          <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </Card>
  );
}
