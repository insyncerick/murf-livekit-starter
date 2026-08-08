import { Store, ShoppingBag, Headphones, Sparkles, RotateCcw, Loader2, Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';

function BazaarStorefrontHeader() {
  return (
    <div className="relative mb-6 flex flex-col items-center">
      <div className="relative flex size-20 items-center justify-center rounded-2xl bg-gradient-to-tr from-amber-500 to-amber-600 shadow-xl shadow-amber-500/20 ring-4 ring-amber-500/10">
        <Store className="size-10 text-white" />
        <div className="absolute -bottom-1 -right-1 flex size-7 items-center justify-center rounded-full bg-emerald-500 text-white ring-2 ring-background">
          <Sparkles className="size-4" />
        </div>
      </div>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText?: string;
  onStartCall: () => void;
  isConnecting?: boolean;
  isCallEnded?: boolean;
  onResetCallEnded?: () => void;
}

export const WelcomeView = ({
  onStartCall,
  isConnecting = false,
  isCallEnded = false,
  onResetCallEnded,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="px-4 py-8 max-w-2xl mx-auto w-full">
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <BazaarStorefrontHeader />

        {/* Branding */}
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
          Bazaar <span className="text-amber-600 dark:text-amber-500">Mitra</span>
        </h1>
        <p className="text-amber-700 dark:text-amber-400 font-semibold text-base mt-1">
          Your AI Assistant for Local Businesses
        </p>
        <p className="text-muted-foreground mt-2 max-w-md text-sm font-medium leading-relaxed">
          Your smart voice assistant to explore local store products, check shop information, and get human support whenever you need it.
        </p>

        {/* State Display: READY / CONNECTING / CALL ENDED */}
        <div className="mt-6 flex flex-col items-center gap-2">
          {isConnecting ? (
            <div className="flex flex-col items-center gap-1.5">
              <span className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-semibold text-blue-600 dark:text-blue-400 animate-pulse">
                <Loader2 className="size-4 animate-spin" />
                Connecting...
              </span>
              <p className="text-xs text-muted-foreground">Please wait while I connect you.</p>
            </div>
          ) : isCallEnded ? (
            <div className="flex flex-col items-center gap-1">
              <span className="inline-flex items-center gap-2 rounded-full border border-slate-500/30 bg-slate-500/10 px-4 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
                <span className="size-2 rounded-full bg-slate-500" />
                Conversation ended
              </span>
            </div>
          ) : (
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
              <span className="size-2 rounded-full bg-emerald-500 animate-ping" />
              Ready to help
            </span>
          )}
        </div>

        {/* Action Button */}
        <div className="mt-6 flex flex-col items-center gap-3">
          {isCallEnded ? (
            <Button
              size="lg"
              onClick={onResetCallEnded}
              className="w-72 rounded-full bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white shadow-lg shadow-amber-500/25 py-6 text-sm font-bold tracking-wider uppercase transition-all duration-300 hover:scale-105 active:scale-95"
            >
              <RotateCcw className="size-4 mr-2" />
              Start Again
            </Button>
          ) : (
            <Button
              size="lg"
              disabled={isConnecting}
              onClick={onStartCall}
              className="w-72 rounded-full bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white shadow-lg shadow-amber-500/25 py-6 text-sm font-bold tracking-wider uppercase transition-all duration-300 hover:scale-105 active:scale-95 disabled:opacity-75"
            >
              {isConnecting ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="size-4 animate-spin" />
                  Connecting...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Mic className="size-4" />
                  Start Conversation
                </span>
              )}
            </Button>
          )}
        </div>

        {/* Small Feature Sections */}
        <div className="mt-10 w-full">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-left">
            <div className="rounded-2xl border border-border/60 bg-card p-4 text-card-foreground shadow-xs transition-all hover:border-amber-500/40">
              <div className="size-9 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-600 dark:text-amber-400 mb-3">
                <ShoppingBag className="size-5" />
              </div>
              <h3 className="font-bold text-sm text-foreground">Products</h3>
              <p className="text-xs text-muted-foreground mt-1 leading-snug">
                Discover local items, prices, and daily store deals.
              </p>
            </div>

            <div className="rounded-2xl border border-border/60 bg-card p-4 text-card-foreground shadow-xs transition-all hover:border-emerald-500/40">
              <div className="size-9 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-3">
                <Store className="size-5" />
              </div>
              <h3 className="font-bold text-sm text-foreground">Store Information</h3>
              <p className="text-xs text-muted-foreground mt-1 leading-snug">
                Check shop hours, locations, and item availability.
              </p>
            </div>

            <div className="rounded-2xl border border-border/60 bg-card p-4 text-card-foreground shadow-xs transition-all hover:border-blue-500/40">
              <div className="size-9 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-600 dark:text-blue-400 mb-3">
                <Headphones className="size-5" />
              </div>
              <h3 className="font-bold text-sm text-foreground">Human Support</h3>
              <p className="text-xs text-muted-foreground mt-1 leading-snug">
                Connect seamlessly with local store owners & staff.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <div className="mt-12 text-center text-xs text-muted-foreground">
        Bazaar Mitra — Voice AI for Local Commerce
      </div>
    </div>
  );
};
