import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ModelType, modelTypes, providers } from '@/data/models';
import { X } from 'lucide-react';

interface FilterBarProps {
  selectedTypes: ModelType[];
  selectedProviders: string[];
  onTypeChange: (types: ModelType[]) => void;
  onProviderChange: (providers: string[]) => void;
}

export function FilterBar({ 
  selectedTypes, 
  selectedProviders, 
  onTypeChange, 
  onProviderChange 
}: FilterBarProps) {
  const toggleType = (type: ModelType) => {
    if (selectedTypes.includes(type)) {
      onTypeChange(selectedTypes.filter(t => t !== type));
    } else {
      onTypeChange([...selectedTypes, type]);
    }
  };

  const toggleProvider = (provider: string) => {
    if (selectedProviders.includes(provider)) {
      onProviderChange(selectedProviders.filter(p => p !== provider));
    } else {
      onProviderChange([...selectedProviders, provider]);
    }
  };

  const clearAll = () => {
    onTypeChange([]);
    onProviderChange([]);
  };

  const hasFilters = selectedTypes.length > 0 || selectedProviders.length > 0;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-4">
        <span className="text-sm font-medium text-muted-foreground">Type:</span>
        <div className="flex flex-wrap gap-2">
          {modelTypes.map((type) => (
            <Badge
              key={type.value}
              variant={selectedTypes.includes(type.value) ? type.value : 'outline'}
              className="cursor-pointer transition-all hover:scale-105"
              onClick={() => toggleType(type.value)}
            >
              {type.label}
            </Badge>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <span className="text-sm font-medium text-muted-foreground">Provider:</span>
        <div className="flex flex-wrap gap-2">
          {providers.map((provider) => (
            <Badge
              key={provider}
              variant={selectedProviders.includes(provider) ? 'default' : 'outline'}
              className="cursor-pointer transition-all hover:scale-105"
              onClick={() => toggleProvider(provider)}
            >
              {provider}
            </Badge>
          ))}
        </div>
      </div>

      {hasFilters && (
        <Button variant="ghost" size="sm" onClick={clearAll} className="text-muted-foreground">
          <X className="h-4 w-4 mr-1" />
          Clear all filters
        </Button>
      )}
    </div>
  );
}
