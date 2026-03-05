import { useRef } from "react";
import { motion, useInView } from "motion/react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StepCardProps {
  num: string;
  image: string;
  caption: string;
  align: "left" | "right";
}

export function StepCard({ num, image, caption, align }: StepCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });

  const fromLeft = align === "left";

  return (
    <div
      ref={ref}
      className={cn("flex", fromLeft ? "justify-start" : "justify-end")}
    >
      <motion.div
        initial={{ opacity: 0, x: fromLeft ? -40 : 40 }}
        animate={isInView ? { opacity: 1, x: 0 } : {}}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <Card className="w-md overflow-hidden py-0 gap-0">
          <img
            src={image}
            alt={caption}
            className="aspect-video w-full object-cover"
          />
          <CardContent className="pt-4 pb-5">
            <motion.p
              className="font-display text-muted-foreground text-sm"
              initial={{ opacity: 0, y: 6 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.15, ease: "easeOut" }}
            >
              {num}
            </motion.p>
            <motion.p
              className="font-body text-lg mt-1"
              initial={{ opacity: 0, y: 6 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.3, ease: "easeOut" }}
            >
              {caption}
            </motion.p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
