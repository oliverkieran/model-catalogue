import { AIModel } from '@/data/models';
import { Button } from './ui/button';
import { ArrowLeftRight, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CompareFloatingBarProps {
  models: AIModel[];
  onOpen: () => void;
  onClear: () => void;
}

export function CompareFloatingBar({ models, onOpen, onClear }: CompareFloatingBarProps) {
  if (models.length === 0) return null;

  return (
    <div 
      className={cn(
        "fixed bottom-6 left-1/2 -translate-x-1/2 z-50",
        "glass rounded-2xl px-6 py-4 shadow-elevated",
        "animate-slide-up"
      )}
    >
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="flex -space-x-2">
            {models.slice(0, 3).map((model, idx) => (
              <div 
                key={model.id}
                className="w-10 h-10 rounded-full bg-secondary border-2 border-background flex items-center justify-center text-xs font-mono font-bold"
                style={{ zIndex: 3 - idx }}
              >
                {model.name.slice(0, 2)}
              </div>
            ))}
          </div>
          <span className="text-sm">
            <span className="font-semibold">{models.length}</span>{' '}
            <span className="text-muted-foreground">model{models.length > 1 ? 's' : ''} selected</span>
          </span>
        </div>

        <div className="h-8 w-px bg-border" />

        <Button 
          variant="hero" 
          size="sm"
          onClick={onOpen}
          disabled={models.length < 2}
        >
          <ArrowLeftRight className="h-4 w-4 mr-2" />
          Compare
        </Button>

        <Button variant="ghost" size="icon" onClick={onClear} className="h-8 w-8">
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
