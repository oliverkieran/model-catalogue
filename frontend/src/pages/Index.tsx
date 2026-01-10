import { useState, useMemo } from "react";
import { Hero } from "@/components/Hero";
import { FilterBar } from "@/components/FilterBar";
import { ModelCard } from "@/components/ModelCard";
import { ModelDetail } from "@/components/ModelDetail";
import { ComparePanel } from "@/components/ComparePanel";
import { CompareFloatingBar } from "@/components/CompareFloatingBar";
import { Helmet } from "react-helmet-async";
import { useModels } from "@/hooks/useModels";
import type { AIModel } from "@/types/api";

const Index = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedOrganizations, setSelectedOrganizations] = useState<string[]>(
    []
  );
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [compareModels, setCompareModels] = useState<AIModel[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  // Fetch models from API
  const { data: models, isLoading, error } = useModels({ limit: 100 });

  // Filter models based on search and filters
  const filteredModels = useMemo(() => {
    if (!models) return [];

    return models.filter((model) => {
      const matchesSearch =
        model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        model.organization.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (model.description?.toLowerCase() || "").includes(
          searchQuery.toLowerCase()
        );

      const matchesOrganization =
        selectedOrganizations.length === 0 ||
        selectedOrganizations.includes(model.organization);

      return matchesSearch && matchesOrganization;
    });
  }, [models, searchQuery, selectedOrganizations]);

  const toggleCompare = (model: AIModel) => {
    setCompareModels((prev) => {
      if (prev.find((m) => m.id === model.id)) {
        return prev.filter((m) => m.id !== model.id);
      }
      if (prev.length >= 4) return prev;
      return [...prev, model];
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading models...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold mb-2 text-destructive">
            Error Loading Models
          </h2>
          <p className="text-muted-foreground mb-4">{error.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // const featuredModels = filteredModels.filter((m) => m.featured);
  // const otherModels = filteredModels.filter((m) => !m.featured);

  return (
    <>
      <Helmet>
        <title>AI Model Catalogue - Compare & Discover AI Models</title>
        <meta
          name="description"
          content="Discover, compare, and choose the perfect AI model for your project. Browse benchmarks, use cases, and expert reviews."
        />
      </Helmet>

      <main className="min-h-screen bg-background">
        <Hero
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
          modelCount={models.length || 0}
        />

        <section className="container py-12">
          <FilterBar
            selectedOrganizations={selectedOrganizations}
            onOrganizationChange={setSelectedOrganizations}
            organizations={Array.from(
              new Set(models?.map((m) => m.organization) || [])
            )}
          />

          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-6">
              Models
              <span className="text-muted-foreground font-normal ml-2">
                ({filteredModels.length})
              </span>
            </h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {filteredModels.map((model, idx) => (
                <div
                  key={model.id}
                  className="animate-slide-up"
                  style={{ animationDelay: `${idx * 0.05}s` }}
                >
                  <ModelCard
                    model={model}
                    onClick={() => setSelectedModel(model)}
                    isComparing={compareModels.some((m) => m.id === model.id)}
                    onCompareToggle={() => toggleCompare(model)}
                  />
                </div>
              ))}
            </div>

            {filteredModels.length === 0 && (
              <div className="text-center py-20">
                <p className="text-xl text-muted-foreground">
                  No models found matching your criteria.
                </p>
                <p className="text-muted-foreground mt-2">
                  Try adjusting your search or filters.
                </p>
              </div>
            )}
          </div>
        </section>

        <ModelDetail
          model={selectedModel}
          onClose={() => setSelectedModel(null)}
        />

        <CompareFloatingBar
          models={compareModels}
          onOpen={() => setIsCompareOpen(true)}
          onClear={() => setCompareModels([])}
        />

        <ComparePanel
          models={compareModels}
          onRemove={(name) =>
            setCompareModels((prev) => prev.filter((m) => m.name !== name))
          }
          onClear={() => setCompareModels([])}
          isOpen={isCompareOpen}
          onOpenChange={setIsCompareOpen}
        />
      </main>
    </>
  );
};

export default Index;
