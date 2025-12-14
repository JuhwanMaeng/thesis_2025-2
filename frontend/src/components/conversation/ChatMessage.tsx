import { cn } from '@/lib/utils';
import { User, Bot } from 'lucide-react';
import { format } from 'date-fns';
import type { Message } from '@/types';
import { Badge } from '@/components/ui/badge';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAgent = message.role === 'agent';

  return (
    <div
      className={cn(
        'flex gap-3 p-4 animate-fade-in',
        isUser ? 'bg-transparent' : 'bg-secondary/30'
      )}
    >
      <div
        className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
          isUser ? 'bg-primary/20' : 'bg-success/20'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-primary" />
        ) : (
          <Bot className="w-4 h-4 text-success" />
        )}
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium">
            {isUser ? 'You' : 'NPC'}
          </span>
          <span className="text-xs text-muted-foreground">
            {format(message.timestamp, 'HH:mm:ss')}
          </span>
          {message.action && (
            <Badge variant="outline" className="text-xs">
              {message.action.action_type}
            </Badge>
          )}
        </div>

        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>

        {message.action && message.action.reason && (
          <div className="text-xs text-muted-foreground italic pt-1">
            Reason: {message.action.reason}
          </div>
        )}
      </div>
    </div>
  );
}
