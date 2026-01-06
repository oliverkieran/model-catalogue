import { Search, X } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChange, placeholder = "Search models..." }: SearchBarProps) {
  return (
    <div className="relative w-full max-w-2xl">
      <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-muted-foreground" />
      </div>
      <Input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full h-14 pl-12 pr-12 text-lg bg-secondary/50 border-border/50 rounded-xl focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-muted-foreground/70"
      />
      {value && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute inset-y-0 right-2 my-auto h-8 w-8"
          onClick={() => onChange('')}
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
