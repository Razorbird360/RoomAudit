import { StepCard } from "@/components/StepCard";
import { CurvedArrow } from "@/components/CurvedArrow";

const steps = [
  {
    num: "01",
    image: "/pipeline/step1.jpg",
    caption: "We start with clean hotel room images",
    align: "left" as const,
  },
  {
    num: "02",
    image: "/pipeline/step2.jpg",
    caption: "SAM3 detects and segments objects in the room",
    align: "right" as const,
  },
  {
    num: "03",
    image: "/pipeline/step3.jpg",
    caption: "FLUX.1 Fill inpaints realistic defects onto detected regions",
    align: "left" as const,
  },
  {
    num: "04",
    image: "/pipeline/step4.jpg",
    caption: "Qwen3-VL inspects the room and returns structured results",
    align: "right" as const,
  },
];

export function HowItWorks() {
  return (
    <div className="flex flex-col py-16 gap-8">
      {steps.map((step, i) => (
        <div key={step.num}>
          <StepCard
            num={step.num}
            image={step.image}
            caption={step.caption}
            align={step.align}
          />
          {i < steps.length - 1 && (
            <CurvedArrow flip={step.align === "right"} />
          )}
        </div>
      ))}
    </div>
  );
}
