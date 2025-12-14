import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toolsApi } from '@/services/api';
import { Wrench, ChevronDown, ChevronUp, Code, Plus, Trash2, Edit2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface ToolsPanelProps {
  className?: string;
}

export function ToolsPanel({ className }: ToolsPanelProps) {
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const queryClient = useQueryClient();

  const { data: toolsData, isLoading } = useQuery({
    queryKey: ['tools'],
    queryFn: () => toolsApi.list(),
  });

  const { data: dynamicTools = [], isLoading: dynamicLoading } = useQuery({
    queryKey: ['dynamic-tools'],
    queryFn: () => toolsApi.listDynamic(),
  });

  const deleteToolMutation = useMutation({
    mutationFn: (toolId: string) => toolsApi.delete(toolId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dynamic-tools'] });
      queryClient.invalidateQueries({ queryKey: ['tools'] });
    },
  });

  const toggleTool = (toolName: string) => {
    setExpandedTools((prev) => ({ ...prev, [toolName]: !prev[toolName] }));
  };

  if (isLoading) {
    return (
      <div className={cn('h-full flex flex-col border-l border-border bg-card', className)}>
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Wrench className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Tools</span>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
          Loading tools...
        </div>
      </div>
    );
  }

  const tools = toolsData?.tools || [];
  const toolNames = toolsData?.tool_names || [];

  const allTools = [...tools, ...dynamicTools.map((dt: any) => ({
    type: 'function',
    function: {
      name: dt.name,
      description: dt.description,
      parameters: dt.parameters_schema,
    },
    isDynamic: true,
    toolId: dt.tool_id,
  }))];

  return (
    <div className={cn('h-full flex flex-col border-l border-border bg-card overflow-hidden', className)}>
      <div className="p-4 border-b border-border shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wrench className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Available Tools</span>
            <Badge variant="outline" className="text-xs">
              {allTools.length}
            </Badge>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setShowCreateDialog(true)}
            className="h-7 px-2"
          >
            <Plus className="w-3 h-3 mr-1" />
            Add
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <Tabs defaultValue="all" className="h-full flex flex-col">
          <TabsList className="mx-4 mt-2">
            <TabsTrigger value="all">All ({allTools.length})</TabsTrigger>
            <TabsTrigger value="dynamic">Dynamic ({dynamicTools.length})</TabsTrigger>
          </TabsList>
          <TabsContent value="all" className="flex-1 overflow-y-auto">
            <div className="p-4 space-y-2">
              {allTools.length === 0 ? (
                <div className="text-center text-sm text-muted-foreground py-8">
                  No tools available
                </div>
              ) : (
                allTools.map((tool: any) => {
              const isExpanded = expandedTools[tool.function?.name || ''];
              const toolName = tool.function?.name || 'unknown';
              const description = tool.function?.description || 'No description';
              const parameters = tool.function?.parameters || {};
              const isDynamic = tool.isDynamic || false;
              const toolId = tool.toolId;

              return (
                <div
                  key={toolName}
                  className="rounded-lg border border-border/50 bg-secondary/50 overflow-hidden group"
                >
                  <div className="flex items-center">
                    <button
                      onClick={() => toggleTool(toolName)}
                      className="flex-1 p-3 flex items-center justify-between hover:bg-secondary/50 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <Code className="w-4 h-4 text-primary" />
                        <span className="text-sm font-mono font-medium">{toolName}</span>
                        {isDynamic && (
                          <Badge variant="secondary" className="text-xs">
                            Dynamic
                          </Badge>
                        )}
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-muted-foreground" />
                      )}
                    </button>
                    {isDynamic && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm(`Delete tool "${toolName}"?`)) {
                            deleteToolMutation.mutate(toolId);
                          }
                        }}
                        className="p-2 opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:bg-destructive/20"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                  {isExpanded && (
                    <div className="px-3 pb-3 space-y-3 border-t border-border/50 pt-3">
                      <div>
                        <div className="text-xs font-medium text-muted-foreground mb-1">Description</div>
                        <div className="text-sm">{description}</div>
                      </div>
                      {parameters.properties && Object.keys(parameters.properties).length > 0 && (
                        <div>
                          <div className="text-xs font-medium text-muted-foreground mb-2">Parameters</div>
                          <div className="space-y-2">
                            {Object.entries(parameters.properties).map(([paramName, paramDef]: [string, any]) => (
                              <div key={paramName} className="bg-background p-2 rounded border border-border/50">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-xs font-mono font-medium">{paramName}</span>
                                  {parameters.required?.includes(paramName) && (
                                    <Badge variant="outline" className="text-xs">
                                      Required
                                    </Badge>
                                  )}
                                  {paramDef.type && (
                                    <Badge variant="secondary" className="text-xs">
                                      {paramDef.type}
                                    </Badge>
                                  )}
                                </div>
                                {paramDef.description && (
                                  <div className="text-xs text-muted-foreground">{paramDef.description}</div>
                                )}
                                {paramDef.enum && (
                                  <div className="text-xs text-muted-foreground mt-1">
                                    Options: {paramDef.enum.join(', ')}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
            </div>
          </TabsContent>
          <TabsContent value="dynamic" className="flex-1 overflow-y-auto">
            <div className="p-4 space-y-2">
              {dynamicTools.length === 0 ? (
                <div className="text-center text-sm text-muted-foreground py-8">
                  No dynamic tools. Click "Add" to create one.
                </div>
              ) : (
                dynamicTools.map((tool: any) => {
                  const isExpanded = expandedTools[tool.name];
                  return (
                    <div
                      key={tool.tool_id}
                      className="rounded-lg border border-border/50 bg-secondary/50 overflow-hidden group"
                    >
                      <div className="flex items-center">
                        <button
                          onClick={() => toggleTool(tool.name)}
                          className="flex-1 p-3 flex items-center justify-between hover:bg-secondary/50 transition-colors"
                        >
                          <div className="flex items-center gap-2">
                            <Code className="w-4 h-4 text-primary" />
                            <span className="text-sm font-mono font-medium">{tool.name}</span>
                            <Badge variant="secondary" className="text-xs">
                              Dynamic
                            </Badge>
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-muted-foreground" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-muted-foreground" />
                          )}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (confirm(`Delete tool "${tool.name}"?`)) {
                              deleteToolMutation.mutate(tool.tool_id);
                            }
                          }}
                          className="p-2 opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:bg-destructive/20"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                      {isExpanded && (
                        <div className="px-3 pb-3 space-y-3 border-t border-border/50 pt-3">
                          <div>
                            <div className="text-xs font-medium text-muted-foreground mb-1">Description</div>
                            <div className="text-sm">{tool.description}</div>
                          </div>
                          {tool.parameters_schema?.properties && (
                            <div>
                              <div className="text-xs font-medium text-muted-foreground mb-2">Parameters</div>
                              <div className="space-y-2">
                                {Object.entries(tool.parameters_schema.properties).map(([paramName, paramDef]: [string, any]) => (
                                  <div key={paramName} className="bg-background p-2 rounded border border-border/50">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="text-xs font-mono font-medium">{paramName}</span>
                                      {tool.parameters_schema.required?.includes(paramName) && (
                                        <Badge variant="outline" className="text-xs">
                                          Required
                                        </Badge>
                                      )}
                                      {paramDef.type && (
                                        <Badge variant="secondary" className="text-xs">
                                          {paramDef.type}
                                        </Badge>
                                      )}
                                    </div>
                                    {paramDef.description && (
                                      <div className="text-xs text-muted-foreground">{paramDef.description}</div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          <div>
                            <div className="text-xs font-medium text-muted-foreground mb-1">Code</div>
                            <pre className="text-xs bg-background p-2 rounded border border-border/50 overflow-x-auto">
                              {tool.code}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </TabsContent>
        </Tabs>
      </ScrollArea>

      <CreateToolDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </div>
  );
}

interface CreateToolDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function CreateToolDialog({ open, onOpenChange }: CreateToolDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [parametersSchema, setParametersSchema] = useState('{"type": "object", "properties": {}, "required": []}');
  const [code, setCode] = useState(`def execute(arguments, context):
    """
    Execute the tool.
    
    Args:
        arguments: Tool arguments from LLM
        context: Execution context (npc_id, world_id, etc.)
    
    Returns:
        Dict with 'success', 'effect', and optionally 'error'
    """
    return {
        "success": True,
        "effect": {}
    }`);
  const queryClient = useQueryClient();

  const createToolMutation = useMutation({
    mutationFn: () => {
      let parsedSchema;
      try {
        parsedSchema = JSON.parse(parametersSchema);
      } catch (e) {
        throw new Error('Invalid JSON schema');
      }
      return toolsApi.create({
        name,
        description,
        parameters_schema: parsedSchema,
        code,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dynamic-tools'] });
      queryClient.invalidateQueries({ queryKey: ['tools'] });
      onOpenChange(false);
      setName('');
      setDescription('');
      setParametersSchema('{"type": "object", "properties": {}, "required": []}');
      setCode(`def execute(arguments, context):
    return {
        "success": True,
        "effect": {}
    }`);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Dynamic Tool</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <Label htmlFor="tool-name">Tool Name *</Label>
            <Input
              id="tool-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="my_custom_action"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Must be unique and not conflict with built-in tools
            </p>
          </div>

          <div>
            <Label htmlFor="tool-description">Description *</Label>
            <Textarea
              id="tool-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What this tool does..."
              rows={3}
            />
          </div>

          <div>
            <Label htmlFor="tool-schema">Parameters Schema (JSON) *</Label>
            <Textarea
              id="tool-schema"
              value={parametersSchema}
              onChange={(e) => setParametersSchema(e.target.value)}
              placeholder='{"type": "object", "properties": {...}, "required": [...]}'
              rows={6}
              className="font-mono text-xs"
            />
          </div>

          <div>
            <Label htmlFor="tool-code">Python Code *</Label>
            <Textarea
              id="tool-code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="def execute(arguments, context): ..."
              rows={12}
              className="font-mono text-xs"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Must define an execute(arguments, context) function that returns a dict with 'success', 'effect', and optionally 'error'
            </p>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => createToolMutation.mutate()}
              disabled={createToolMutation.isPending || !name || !description || !code}
            >
              {createToolMutation.isPending ? 'Creating...' : 'Create Tool'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
