import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { X } from "lucide-react";

interface FilterBarProps {
  selectedOrganizations: string[];
  onOrganizationChange: (organizations: string[]) => void;
  organizations: string[];
}

export function FilterBar({
  selectedOrganizations,
  onOrganizationChange,
  organizations,
}: FilterBarProps) {
  const toggleOrganization = (organization: string) => {
    if (selectedOrganizations.includes(organization)) {
      onOrganizationChange(
        selectedOrganizations.filter((o) => o !== organization)
      );
    } else {
      onOrganizationChange([...selectedOrganizations, organization]);
    }
  };

  const clearAll = () => {
    onOrganizationChange([]);
  };

  const hasFilters = selectedOrganizations.length > 0;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-4">
        <span className="text-sm font-medium text-muted-foreground">Type:</span>
        <div className="flex flex-wrap gap-2">
          {organizations.map((organization) => (
            <Badge
              key={organization}
              variant="outline"
              className="cursor-pointer transition-all hover:scale-105"
              onClick={() => toggleOrganization(organization)}
            >
              {organization}
            </Badge>
          ))}
        </div>
      </div>

      {hasFilters && (
        <Button
          variant="ghost"
          size="sm"
          onClick={clearAll}
          className="text-muted-foreground"
        >
          <X className="h-4 w-4 mr-1" />
          Clear all filters
        </Button>
      )}
    </div>
  );
}
