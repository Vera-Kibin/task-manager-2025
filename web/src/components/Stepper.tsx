import React from "react";

type StepperProps<T extends string> = {
  values: readonly T[];
  value: T;
  onChange: (v: T) => void;
  className?: string;
};

export function Stepper<T extends string>({
  values,
  value,
  onChange,
  className,
}: StepperProps<T>) {
  const idx = values.indexOf(value);
  const prev = () =>
    onChange(values[(idx - 1 + values.length) % values.length]);
  const next = () => onChange(values[(idx + 1) % values.length]);

  return (
    <div
      className={`inline-flex items-center rounded-lg border border-slate-300 bg-white ${className || ""}`}
    >
      <button
        type="button"
        className="px-2 py-1 hover:bg-slate-100"
        onClick={prev}
        aria-label="Previous"
      >
        ‹
      </button>
      <div className="px-3 py-1 min-w-[6.5rem] text-center font-medium">
        {value}
      </div>
      <button
        type="button"
        className="px-2 py-1 hover:bg-slate-100"
        onClick={next}
        aria-label="Next"
      >
        ›
      </button>
    </div>
  );
}

type StepperNullableProps<T extends string> = {
  values: readonly T[];
  value?: T;
  onChange: (v: T | undefined) => void;
  placeholder: string;
  className?: string;
};

export function StepperNullable<T extends string>({
  values,
  value,
  onChange,
  placeholder,
  className,
}: StepperNullableProps<T>) {
  const idx = value ? values.indexOf(value) : -1;
  const prev = () => {
    if (idx === -1) onChange(values[values.length - 1]);
    else if (idx === 0) onChange(undefined);
    else onChange(values[idx - 1]);
  };
  const next = () => {
    if (idx === -1) onChange(values[0]);
    else if (idx === values.length - 1) onChange(undefined);
    else onChange(values[idx + 1]);
  };
  const label = value ?? (placeholder as any);

  return (
    <div
      className={`inline-flex items-center rounded-lg border border-slate-300 bg-white ${className || ""}`}
    >
      <button
        type="button"
        className="px-2 py-1 hover:bg-slate-100"
        onClick={prev}
        aria-label="Previous"
      >
        ‹
      </button>
      <div className="px-3 py-1 min-w-[9.5rem] text-center">{label}</div>
      <button
        type="button"
        className="px-2 py-1 hover:bg-slate-100"
        onClick={next}
        aria-label="Next"
      >
        ›
      </button>
    </div>
  );
}
