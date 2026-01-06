import { SearchBar } from './SearchBar';
import { Sparkles, Cpu, Brain, Layers } from 'lucide-react';

interface HeroProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  modelCount: number;
}

export function Hero({ searchValue, onSearchChange, modelCount }: HeroProps) {
  return (
    <section className="relative py-20 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent/10 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
      </div>

      <div className="container relative z-10">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Floating icons */}
          <div className="flex justify-center gap-6 mb-6">
            <div className="p-3 rounded-xl bg-model-language/10 text-model-language animate-float" style={{ animationDelay: '0s' }}>
              <Brain className="h-6 w-6" />
            </div>
            <div className="p-3 rounded-xl bg-model-vision/10 text-model-vision animate-float" style={{ animationDelay: '0.5s' }}>
              <Cpu className="h-6 w-6" />
            </div>
            <div className="p-3 rounded-xl bg-model-multimodal/10 text-model-multimodal animate-float" style={{ animationDelay: '1s' }}>
              <Layers className="h-6 w-6" />
            </div>
          </div>

          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight">
            <span className="text-gradient-primary">AI Model</span>{' '}
            <span className="text-foreground">Catalogue</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
            Discover, compare, and choose the perfect AI model for your next project.
            <span className="text-primary font-medium"> {modelCount} models</span> and counting.
          </p>

          <div className="flex justify-center pt-4">
            <SearchBar 
              value={searchValue}
              onChange={onSearchChange}
              placeholder="Search by model name, provider, or capability..."
            />
          </div>

          <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground pt-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <span>Updated daily</span>
            </div>
            <div className="h-4 w-px bg-border" />
            <span>Benchmarks • Use Cases • Reviews</span>
          </div>
        </div>
      </div>
    </section>
  );
}
