import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { worldApi } from '@/services/api';
import type { WorldKnowledge, NPC } from '@/types';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Globe, Plus, Trash2, Edit2, AlertTriangle, X } from 'lucide-react';

export function WorldsPage() {
  const [selectedWorldId, setSelectedWorldId] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [worldToDelete, setWorldToDelete] = useState<WorldKnowledge | null>(null);
  const queryClient = useQueryClient();

  const { data: worlds = [], isLoading: worldsLoading } = useQuery<WorldKnowledge[]>({
    queryKey: ['worlds'],
    queryFn: () => worldApi.list(),
  });

  const { data: selectedWorld } = useQuery<WorldKnowledge>({
    queryKey: ['world', selectedWorldId],
    queryFn: () => worldApi.get(selectedWorldId!),
    enabled: !!selectedWorldId && showEditDialog,
  });

  const { data: worldNpcs = [] } = useQuery<NPC[]>({
    queryKey: ['world-npcs', worldToDelete?.world_id],
    queryFn: () => worldApi.getNpcs(worldToDelete!.world_id),
    enabled: !!worldToDelete?.world_id,
  });

  const deleteWorldMutation = useMutation({
    mutationFn: ({ worldId, deleteNpcs }: { worldId: string; deleteNpcs: boolean }) =>
      worldApi.delete(worldId, deleteNpcs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['worlds'] });
      queryClient.invalidateQueries({ queryKey: ['npcs'] });
      setShowDeleteDialog(false);
      setWorldToDelete(null);
      if (selectedWorldId === worldToDelete?.world_id) {
        setSelectedWorldId(null);
      }
    },
  });

  const handleDeleteClick = (world: WorldKnowledge) => {
    setWorldToDelete(world);
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = (deleteNpcs: boolean) => {
    if (worldToDelete) {
      deleteWorldMutation.mutate({
        worldId: worldToDelete.world_id,
        deleteNpcs,
      });
    }
  };

  return (
    <div className="h-full w-full flex flex-col overflow-hidden bg-background">
      <div className="p-6 border-b border-border shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Worlds</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage game worlds and their settings
            </p>
          </div>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create World
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-6">
          {worldsLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : worlds.length === 0 ? (
            <div className="text-center py-12">
              <Globe className="w-16 h-16 mx-auto mb-4 opacity-50 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">No worlds yet. Create one to get started.</p>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create World
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {worlds.map((world) => (
                <Card
                  key={world.world_id}
                  className="p-4 cursor-pointer hover:bg-secondary/50 transition-colors"
                  onClick={() => {
                    setSelectedWorldId(world.world_id);
                    setShowEditDialog(true);
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <Globe className="w-5 h-5 text-primary shrink-0" />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold truncate">{world.title}</h3>
                        <p className="text-xs text-muted-foreground truncate">{world.world_id}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedWorldId(world.world_id);
                          setShowEditDialog(true);
                        }}
                        className="p-1 rounded hover:bg-secondary"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteClick(world);
                        }}
                        className="p-1 rounded hover:bg-destructive/20 text-destructive"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  {world.locations && Object.keys(world.locations).length > 0 && (
                    <div className="text-xs text-muted-foreground mt-2">
                      {Object.keys(world.locations).length} location(s)
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* 월드 생성 다이얼로그 */}
      <CreateWorldDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSuccess={() => {
          setShowCreateDialog(false);
          queryClient.invalidateQueries({ queryKey: ['worlds'] });
        }}
      />

      {/* 월드 수정 다이얼로그 */}
      {selectedWorldId && selectedWorld && (
        <EditWorldDialog
          world={selectedWorld}
          open={showEditDialog}
          onOpenChange={setShowEditDialog}
          onSuccess={() => {
            setShowEditDialog(false);
            queryClient.invalidateQueries({ queryKey: ['worlds'] });
            queryClient.invalidateQueries({ queryKey: ['world', selectedWorldId] });
          }}
        />
      )}

      {/* 월드 삭제 확인 다이얼로그 */}
      <DeleteWorldDialog
        world={worldToDelete}
        npcCount={worldToDelete ? worldNpcs.length : 0}
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        onConfirm={handleDeleteConfirm}
        isDeleting={deleteWorldMutation.isPending}
      />
    </div>
  );
}

function CreateWorldDialog({
  open,
  onOpenChange,
  onSuccess,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}) {
  const [title, setTitle] = useState('');
  const [worldId, setWorldId] = useState('');
  const [laws, setLaws] = useState('');
  const [socialNorms, setSocialNorms] = useState('');
  const [locations, setLocations] = useState<Record<string, Record<string, any>>>({});
  const [showLocationDialog, setShowLocationDialog] = useState(false);
  const [editingLocation, setEditingLocation] = useState<{ name: string; data: Record<string, any> } | null>(null);
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: worldApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['worlds'] });
      onSuccess();
      setTitle('');
      setWorldId('');
      setLaws('');
      setSocialNorms('');
      setLocations({});
    },
  });

  const handleSubmit = () => {
    if (!title.trim()) {
      alert('Title is required');
      return;
    }

    const rules: Record<string, any> = {};
    if (laws.trim()) {
      rules.laws = laws.split('\n').filter(l => l.trim());
    }
    if (socialNorms.trim()) {
      rules.social_norms = socialNorms.split('\n').filter(n => n.trim());
    }

    createMutation.mutate({
      world_id: worldId.trim() || undefined,
      title: title.trim(),
      rules: Object.keys(rules).length > 0 ? rules : undefined,
      locations: Object.keys(locations).length > 0 ? locations : undefined,
    });
  };

  const handleAddLocation = () => {
    setEditingLocation(null);
    setShowLocationDialog(true);
  };

  const handleEditLocation = (name: string) => {
    setEditingLocation({ name, data: locations[name] });
    setShowLocationDialog(true);
  };

  const handleDeleteLocation = (name: string) => {
    const newLocations = { ...locations };
    delete newLocations[name];
    setLocations(newLocations);
  };

  const handleLocationSave = (oldName: string | null, newName: string, data: Record<string, any>) => {
    const newLocations = { ...locations };
    if (oldName && oldName !== newName) {
      delete newLocations[oldName];
    }
    newLocations[newName] = data;
    setLocations(newLocations);
    setShowLocationDialog(false);
    setEditingLocation(null);
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New World</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="world-title">Title *</Label>
              <Input
                id="world-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Fantasy Realm"
              />
            </div>
            <div>
              <Label htmlFor="world-id">World ID (Optional)</Label>
              <Input
                id="world-id"
                value={worldId}
                onChange={(e) => setWorldId(e.target.value)}
                placeholder="world_001 (auto-generated if empty)"
              />
            </div>
            <div>
              <Label htmlFor="laws">Laws (one per line)</Label>
              <Textarea
                id="laws"
                value={laws}
                onChange={(e) => setLaws(e.target.value)}
                placeholder="No violence in towns&#10;Respect magic users"
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="norms">Social Norms (one per line)</Label>
              <Textarea
                id="norms"
                value={socialNorms}
                onChange={(e) => setSocialNorms(e.target.value)}
                placeholder="Greet with respect&#10;Offer help to travelers"
                rows={4}
              />
            </div>
            
            {/* Locations Section */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Locations</Label>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={handleAddLocation}
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Location
                </Button>
              </div>
              {Object.keys(locations).length === 0 ? (
                <p className="text-sm text-muted-foreground py-2">No locations added</p>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto p-2 border rounded-lg">
                  {Object.entries(locations).map(([name, data]) => (
                    <div
                      key={name}
                      className="flex items-center justify-between p-2 rounded border bg-secondary/30"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm">{name}</div>
                        <div className="text-xs text-muted-foreground">
                          {data.type && `Type: ${data.type}`}
                          {data.population && ` • Population: ${data.population}`}
                        </div>
                      </div>
                      <div className="flex gap-1 ml-2">
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEditLocation(name)}
                        >
                          <Edit2 className="w-3 h-3" />
                        </Button>
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteLocation(name)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button 
                variant="outline" 
                onClick={() => onOpenChange(false)}
                disabled={createMutation.isPending}
              >
                Cancel
              </Button>
              <Button 
                onClick={handleSubmit} 
                disabled={createMutation.isPending || !title.trim()}
              >
                {createMutation.isPending ? 'Creating...' : 'Create World'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Location Edit Dialog */}
      <LocationEditDialog
        open={showLocationDialog}
        onOpenChange={setShowLocationDialog}
        location={editingLocation}
        onSave={handleLocationSave}
      />
    </>
  );
}

function EditWorldDialog({
  world,
  open,
  onOpenChange,
  onSuccess,
}: {
  world: WorldKnowledge;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}) {
  const [title, setTitle] = useState(world.title);
  const [laws, setLaws] = useState(
    world.rules?.laws ? world.rules.laws.join('\n') : ''
  );
  const [socialNorms, setSocialNorms] = useState(
    world.rules?.social_norms ? world.rules.social_norms.join('\n') : ''
  );
  const [locations, setLocations] = useState<Record<string, Record<string, any>>>(
    world.locations || {}
  );
  const [showLocationDialog, setShowLocationDialog] = useState(false);
  const [editingLocation, setEditingLocation] = useState<{ name: string; data: Record<string, any> } | null>(null);
  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: (updates: Partial<WorldKnowledge>) => worldApi.update(world.world_id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['worlds'] });
      queryClient.invalidateQueries({ queryKey: ['world', world.world_id] });
      onSuccess();
    },
  });

  const handleSubmit = () => {
    const rules: Record<string, any> = { ...world.rules };
    if (laws.trim()) {
      rules.laws = laws.split('\n').filter(l => l.trim());
    } else {
      delete rules.laws;
    }
    if (socialNorms.trim()) {
      rules.social_norms = socialNorms.split('\n').filter(n => n.trim());
    } else {
      delete rules.social_norms;
    }

    updateMutation.mutate({
      title: title.trim(),
      rules,
      locations: Object.keys(locations).length > 0 ? locations : undefined,
    });
  };

  const handleAddLocation = () => {
    setEditingLocation(null);
    setShowLocationDialog(true);
  };

  const handleEditLocation = (name: string) => {
    setEditingLocation({ name, data: locations[name] });
    setShowLocationDialog(true);
  };

  const handleDeleteLocation = (name: string) => {
    const newLocations = { ...locations };
    delete newLocations[name];
    setLocations(newLocations);
  };

  const handleLocationSave = (oldName: string | null, newName: string, data: Record<string, any>) => {
    const newLocations = { ...locations };
    if (oldName && oldName !== newName) {
      delete newLocations[oldName];
    }
    newLocations[newName] = data;
    setLocations(newLocations);
    setShowLocationDialog(false);
    setEditingLocation(null);
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit World: {world.title}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-title">Title *</Label>
              <Input
                id="edit-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="edit-laws">Laws (one per line)</Label>
              <Textarea
                id="edit-laws"
                value={laws}
                onChange={(e) => setLaws(e.target.value)}
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="edit-norms">Social Norms (one per line)</Label>
              <Textarea
                id="edit-norms"
                value={socialNorms}
                onChange={(e) => setSocialNorms(e.target.value)}
                rows={4}
              />
            </div>
            
            {/* Locations Section */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Locations</Label>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={handleAddLocation}
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Location
                </Button>
              </div>
              {Object.keys(locations).length === 0 ? (
                <p className="text-sm text-muted-foreground py-2">No locations added</p>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto p-2 border rounded-lg">
                  {Object.entries(locations).map(([name, data]) => (
                    <div
                      key={name}
                      className="flex items-center justify-between p-2 rounded border bg-secondary/30"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm">{name}</div>
                        <div className="text-xs text-muted-foreground">
                          {data.type && `Type: ${data.type}`}
                          {data.population && ` • Population: ${data.population}`}
                        </div>
                      </div>
                      <div className="flex gap-1 ml-2">
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEditLocation(name)}
                        >
                          <Edit2 className="w-3 h-3" />
                        </Button>
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteLocation(name)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button 
                variant="outline" 
                onClick={() => onOpenChange(false)}
                disabled={updateMutation.isPending}
              >
                Cancel
              </Button>
              <Button 
                onClick={handleSubmit} 
                disabled={updateMutation.isPending || !title.trim()}
              >
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Location Edit Dialog */}
      <LocationEditDialog
        open={showLocationDialog}
        onOpenChange={setShowLocationDialog}
        location={editingLocation}
        onSave={handleLocationSave}
      />
    </>
  );
}

function LocationEditDialog({
  open,
  onOpenChange,
  location,
  onSave,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  location: { name: string; data: Record<string, any> } | null;
  onSave: (oldName: string | null, newName: string, data: Record<string, any>) => void;
}) {
  const [name, setName] = useState(location?.name || '');
  const [type, setType] = useState(location?.data?.type || '');
  const [population, setPopulation] = useState(location?.data?.population || '');
  const [description, setDescription] = useState(location?.data?.description || '');
  const [customFields, setCustomFields] = useState<Array<{ key: string; value: string }>>(() => {
    if (!location?.data) return [];
    const fields: Array<{ key: string; value: string }> = [];
    Object.entries(location.data).forEach(([key, value]) => {
      if (!['type', 'population', 'description'].includes(key)) {
        fields.push({ key, value: String(value) });
      }
    });
    return fields;
  });

  const resetForm = () => {
    setName('');
    setType('');
    setPopulation('');
    setDescription('');
    setCustomFields([]);
  };

  const handleSave = () => {
    if (!name.trim()) {
      alert('Location name is required');
      return;
    }

    const data: Record<string, any> = {};
    if (type.trim()) data.type = type.trim();
    if (population.trim()) data.population = population.trim();
    if (description.trim()) data.description = description.trim();
    
    customFields.forEach(({ key, value }) => {
      if (key.trim() && value.trim()) {
        data[key.trim()] = value.trim();
      }
    });

    onSave(location?.name || null, name.trim(), data);
    resetForm();
  };

  const handleClose = (open: boolean) => {
    if (!open) {
      resetForm();
    }
    onOpenChange(open);
  };

  const handleAddCustomField = () => {
    setCustomFields([...customFields, { key: '', value: '' }]);
  };

  const handleRemoveCustomField = (index: number) => {
    setCustomFields(customFields.filter((_, i) => i !== index));
  };

  const handleCustomFieldChange = (index: number, field: 'key' | 'value', value: string) => {
    const newFields = [...customFields];
    newFields[index][field] = value;
    setCustomFields(newFields);
  };

  // Update form when location changes or dialog opens
  useEffect(() => {
    if (open) {
      if (location) {
        setName(location.name);
        setType(location.data?.type || '');
        setPopulation(location.data?.population || '');
        setDescription(location.data?.description || '');
        const fields: Array<{ key: string; value: string }> = [];
        Object.entries(location.data || {}).forEach(([key, value]) => {
          if (!['type', 'population', 'description'].includes(key)) {
            fields.push({ key, value: String(value) });
          }
        });
        setCustomFields(fields);
      } else {
        resetForm();
      }
    }
  }, [location, open]);

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{location ? 'Edit Location' : 'Add Location'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <Label htmlFor="location-name">Location Name *</Label>
            <Input
              id="location-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="shire"
            />
          </div>
          <div>
            <Label htmlFor="location-type">Type</Label>
            <Input
              id="location-type"
              value={type}
              onChange={(e) => setType(e.target.value)}
              placeholder="peaceful"
            />
          </div>
          <div>
            <Label htmlFor="location-population">Population</Label>
            <Input
              id="location-population"
              value={population}
              onChange={(e) => setPopulation(e.target.value)}
              placeholder="hobbits"
            />
          </div>
          <div>
            <Label htmlFor="location-description">Description</Label>
            <Textarea
              id="location-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="A peaceful farming community"
              rows={3}
            />
          </div>

          {/* Custom Fields */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <Label>Additional Properties</Label>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleAddCustomField}
              >
                <Plus className="w-3 h-3 mr-1" />
                Add Field
              </Button>
            </div>
            {customFields.length === 0 ? (
              <p className="text-sm text-muted-foreground py-2">No additional properties</p>
            ) : (
              <div className="space-y-2">
                {customFields.map((field, index) => (
                  <div key={index} className="flex gap-2 items-center">
                    <Input
                      placeholder="Key"
                      value={field.key}
                      onChange={(e) => handleCustomFieldChange(index, 'key', e.target.value)}
                      className="flex-1"
                    />
                    <Input
                      placeholder="Value"
                      value={field.value}
                      onChange={(e) => handleCustomFieldChange(index, 'value', e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRemoveCustomField(index)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-border">
            <Button 
              variant="outline" 
              onClick={() => handleClose(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleSave}>
              {location ? 'Save Changes' : 'Add Location'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function DeleteWorldDialog({
  world,
  npcCount,
  open,
  onOpenChange,
  onConfirm,
  isDeleting,
}: {
  world: WorldKnowledge | null;
  npcCount: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (deleteNpcs: boolean) => void;
  isDeleting: boolean;
}) {
  const [deleteNpcs, setDeleteNpcs] = useState(false);

  if (!world) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete World</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              <span>Are you sure you want to delete "{world.title}"?</span>
            </div>
          </div>

          {npcCount > 0 && (
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-600 dark:text-yellow-400">
                This world has <strong>{npcCount} NPC(s)</strong>. Deleting this world will also delete all NPCs in it.
              </div>
              <div className="flex items-center gap-2 p-3 rounded-lg border border-border bg-secondary/50">
                <input
                  type="checkbox"
                  id="delete-npcs"
                  checked={deleteNpcs}
                  onChange={(e) => setDeleteNpcs(e.target.checked)}
                  className="rounded"
                />
                <Label htmlFor="delete-npcs" className="cursor-pointer">
                  Also delete {npcCount} NPC(s) in this world
                </Label>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-4 border-t border-border">
            <Button 
              variant="outline" 
              onClick={() => onOpenChange(false)} 
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => onConfirm(deleteNpcs)}
              disabled={isDeleting || (npcCount > 0 && !deleteNpcs)}
            >
              {isDeleting ? 'Deleting...' : 'Delete World'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
