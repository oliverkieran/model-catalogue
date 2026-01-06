import { useState, useMemo } from 'react';
import { Hero } from '@/components/Hero';
import { FilterBar } from '@/components/FilterBar';
import { ModelCard } from '@/components/ModelCard';
import { ModelDetail } from '@/components/ModelDetail';
import { ComparePanel } from '@/components/ComparePanel';
import { CompareFloatingBar } from '@/components/CompareFloatingBar';
import { models, AIModel, ModelType } from '@/data/models';
import { Helmet } from 'react-helmet-async';

const Index = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<ModelType[]>([]);
  const [selectedProviders, setSelectedProviders] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [compareModels, setCompareModels] = useState<AIModel[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  const filteredModels = useMemo(() => {
    return models.filter((model) => {
      const matchesSearch = 
        model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        model.provider.toLowerCase().includes(searchQuery.toLowerCase()) ||
        model.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        model.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesType = selectedTypes.length === 0 || selectedTypes.includes(model.type);
      const matchesProvider = selectedProviders.length === 0 || selectedProviders.includes(model.provider);

      return matchesSearch && matchesType && matchesProvider;
    });
  }, [searchQuery, selectedTypes, selectedProviders]);

  const toggleCompare = (model: AIModel) => {
    setCompareModels((prev) => {
      if (prev.find(m => m.id === model.id)) {
        return prev.filter(m => m.id !== model.id);
      }
      if (prev.length >= 4) return prev;
      return [...prev, model];
    });
  };

  const featuredModels = filteredModels.filter(m => m.featured);
  const otherModels = filteredModels.filter(m => !m.featured);

  return (
    <>
      <Helmet>
        <title>AI Model Catalogue - Compare & Discover AI Models</title>
        <meta name="description" content="Discover, compare, and choose the perfect AI model for your project. Browse benchmarks, use cases, and expert reviews for GPT-4, Claude, Gemini, and more." />
      </Helmet>

      <main className="min-h-screen bg-background">
        <Hero 
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
          modelCount={models.length}
        />

        <section className="container py-12">
          <FilterBar
            selectedTypes={selectedTypes}
            selectedProviders={selectedProviders}
            onTypeChange={setSelectedTypes}
            onProviderChange={setSelectedProviders}
          />

          {featuredModels.length > 0 && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span className="text-gradient-primary">Featured</span> Models
              </h2>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {featuredModels.map((model, idx) => (
                  <div 
                    key={model.id} 
                    className="animate-slide-up"
                    style={{ animationDelay: `${idx * 0.1}s` }}
                  >
                    <ModelCard
                      model={model}
                      onClick={() => setSelectedModel(model)}
                      isComparing={compareModels.some(m => m.id === model.id)}
                      onCompareToggle={() => toggleCompare(model)}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-6">
              {featuredModels.length > 0 ? 'All Models' : 'Models'}
              <span className="text-muted-foreground font-normal ml-2">
                ({filteredModels.length})
              </span>
            </h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {(featuredModels.length > 0 ? otherModels : filteredModels).map((model, idx) => (
                <div 
                  key={model.id} 
                  className="animate-slide-up"
                  style={{ animationDelay: `${idx * 0.05}s` }}
                >
                  <ModelCard
                    model={model}
                    onClick={() => setSelectedModel(model)}
                    isComparing={compareModels.some(m => m.id === model.id)}
                    onCompareToggle={() => toggleCompare(model)}
                  />
                </div>
              ))}
            </div>

            {filteredModels.length === 0 && (
              <div className="text-center py-20">
                <p className="text-xl text-muted-foreground">No models found matching your criteria.</p>
                <p className="text-muted-foreground mt-2">Try adjusting your search or filters.</p>
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
          onRemove={(id) => setCompareModels(prev => prev.filter(m => m.id !== id))}
          onClear={() => setCompareModels([])}
          isOpen={isCompareOpen}
          onOpenChange={setIsCompareOpen}
        />
      </main>
    </>
  );
};

export default Index;
