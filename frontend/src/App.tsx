import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Toaster } from "@/components/ui/sonner";
import { AnimatedGridPattern } from "@/components/ui/animated-grid-pattern";
import { HowItWorks } from "@/components/HowItWorks";
import { Inspect } from "@/components/Inspect";
import { cn } from "@/lib/utils";

function App() {
  return (
    <div className="relative min-h-screen bg-background py-12 px-4 overflow-hidden">
      <AnimatedGridPattern
        numSquares={40}
        maxOpacity={0.1}
        duration={3}
        repeatDelay={1}
        className={cn(
          "fixed inset-0 h-screen w-screen skew-y-12",
          "[mask-image:radial-gradient(800px_circle_at_center,white,transparent)]",
        )}
      />

      <div className="relative z-10">
        <header className="text-center mb-10">
          <h1 className="font-display text-3xl text-foreground">RoomAudit</h1>
          <p className="text-muted-foreground text-sm font-body mt-1">
            AI hotel room inspection
          </p>
        </header>

        <Tabs defaultValue="how-it-works" className="mx-auto max-w-4xl">
          <TabsList variant="line" className="mx-auto">
            <TabsTrigger value="how-it-works">How It Works</TabsTrigger>
            <TabsTrigger value="inspect">Inspect</TabsTrigger>
          </TabsList>

          <TabsContent value="how-it-works">
            <HowItWorks />
          </TabsContent>

          <TabsContent value="inspect">
            <Inspect />
          </TabsContent>
        </Tabs>
      </div>

      <Toaster />
    </div>
  );
}

export default App;
