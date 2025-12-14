import { Sun, Moon, Wrench } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  onToolsToggle: () => void;
  showTools?: boolean;
}

export function Header({ onToolsToggle, showTools }: HeaderProps) {
  const [isDark, setIsDark] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  return (
    <header className="h-12 flex items-center justify-between px-4 border-b border-border bg-card shrink-0">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
            <span className="text-xs font-bold text-primary-foreground">AI</span>
          </div>
          <span className="text-sm font-semibold">AI NPC Framework</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant={showTools ? 'default' : 'ghost'}
          size="icon"
          onClick={onToolsToggle}
          title={onToolsToggle ? "Toggle Tools Panel" : "Open Tools"}
        >
          <Wrench className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsDark(!isDark)}
          title={isDark ? 'Light mode' : 'Dark mode'}
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>
      </div>
    </header>
  );
}
