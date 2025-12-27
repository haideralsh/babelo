import * as Headless from "@headlessui/react";
import clsx from "clsx";
import React, { forwardRef } from "react";

export const Textarea = forwardRef(function Textarea(
  {
    className,
    resizable = true,
    ...props
  }: { className?: string; resizable?: boolean } & Omit<
    Headless.TextareaProps,
    "as" | "className"
  >,
  ref: React.ForwardedRef<HTMLTextAreaElement>
) {
  return (
    <span
      data-slot="control"
      className={clsx([
        className,
        // Basic layout
        "relative block w-full",
        // Background color + shadow applied to inset pseudo element, so shadow blends with border in light mode
        "before:absolute before:inset-px before:bg-white",
        // Focus ring
        // "after:pointer-events-none after:absolute after:inset-0 after:ring-transparent after:ring-inset sm:focus-within:after:ring-2 sm:focus-within:after:ring-blue-500",
        // Disabled state
        "has-data-disabled:opacity-90 has-data-disabled:before:bg-zinc-950/5",
      ])}
    >
      <Headless.Textarea
        ref={ref}
        {...props}
        className={clsx([
          // Basic layout
          "relative block h-full w-full appearance-none px-[calc(--spacing(4)-1px)] py-[calc(--spacing(4)-1px)] sm:px-[calc(--spacing(4)-1px)] sm:py-[calc(--spacing(4)-1px)]",
          // Typography
          "font-['Noto_Sans'] text-2xl text-zinc-950 placeholder:text-zinc-500",
          // Border
          "border-none",
          // Background color
          "bg-transparent",
          // Hide default focus styles
          "focus:outline-hidden",
          // Invalid state
          "data-invalid:border-red-500",
          // Disabled state
          "disabled:opacity-100",
          // Resizable
          resizable ? "resize-y" : "resize-none",
        ])}
      />
    </span>
  );
});
