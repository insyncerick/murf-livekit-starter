import { ReactNode, useEffect } from 'react';
import { toast as sonnerToast } from 'sonner';
import { useAgent, useSessionContext } from '@livekit/components-react';
import { WarningIcon, MicrophoneSlash } from '@phosphor-icons/react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface ToastProps {
  title: ReactNode;
  description: ReactNode;
  icon?: ReactNode;
}

export function toastAlert(toast: ToastProps) {
  const { title, description, icon } = toast;

  return sonnerToast.custom(
    (id) => (
      <Alert onClick={() => sonnerToast.dismiss(id)} className="bg-accent border-destructive/30 w-full md:w-[380px]">
        {icon ?? <WarningIcon weight="bold" />}
        <AlertTitle>{title}</AlertTitle>
        {description && <AlertDescription>{description}</AlertDescription>}
      </Alert>
    ),
    { duration: 12_000 }
  );
}

export function showMicPermissionErrorToast(onRetry?: () => void) {
  toastAlert({
    title: 'Microphone Access Required',
    icon: <MicrophoneSlash weight="bold" className="text-destructive size-5 shrink-0" />,
    description: (
      <div className="text-xs space-y-2 mt-1">
        <p className="font-medium text-foreground leading-relaxed">
          Microphone access is required to talk to Bazaar Mitra. Please allow microphone access in your browser settings and try again.
        </p>
        <Button
          size="sm"
          variant="outline"
          onClick={(e) => {
            e.stopPropagation();
            sonnerToast.dismiss();
            onRetry?.();
            window.location.reload();
          }}
          className="mt-1 h-7 text-xs border-destructive/40 hover:bg-destructive/10"
        >
          Try Again
        </Button>
      </div>
    ),
  });
}

export function useAgentErrors() {
  const agent = useAgent();
  const session = useSessionContext();
  const { isConnected, end } = session;

  useEffect(() => {
    if (isConnected && agent.state === 'failed') {
      const reasons = agent.failureReasons;

      toastAlert({
        title: 'Session ended',
        description: (
          <>
            {reasons.length > 1 && (
              <ul className="list-inside list-disc">
                {reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            )}
            {reasons.length === 1 && <p className="w-full">{reasons[0]}</p>}
            <p className="w-full">
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://docs.livekit.io/agents/start/voice-ai/"
                className="whitespace-nowrap underline"
              >
                See quickstart guide
              </a>
              .
            </p>
          </>
        ),
      });

      end();
    }
  }, [agent, isConnected, end]);
}
