import { ChevronLeft, ChevronRight, Search, TrendingDown, TrendingUp } from "lucide-react";
import type { ComponentProps, ElementType, ReactNode } from "react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";

import { cn } from "@/lib/utils";

export function Btn({
  variant = "primary",
  className,
  ...props
}: ComponentProps<"button"> & { variant?: "primary" | "secondary" | "ghost" | "danger" }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md px-4 py-[10px] text-sm font-semibold transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" &&
          "bg-primary text-primary-foreground hover:brightness-110 active:brightness-90",
        variant === "secondary" &&
          "border border-border bg-secondary text-foreground hover:bg-border",
        variant === "ghost" &&
          "border border-primary bg-transparent text-primary hover:bg-primary/10 active:bg-primary/20",
        variant === "danger" && "bg-destructive text-destructive-foreground hover:brightness-110",
        className,
      )}
      {...props}
    />
  );
}

export function Field({ className, ...props }: ComponentProps<"input">) {
  return (
    <input
      className={cn(
        "h-10 w-full rounded-md border border-border bg-input px-3 py-[10px] text-sm text-foreground transition-all duration-150 outline-none placeholder:text-muted-foreground focus:border-primary focus:ring-[3px] focus:ring-primary/10 disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

export function SearchField({ className, ...props }: ComponentProps<"input">) {
  return (
    <div className={cn("relative", className)}>
      <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
      <Field className="pl-9" placeholder="Search..." {...props} />
    </div>
  );
}

export function Select({ className, ...props }: ComponentProps<"select">) {
  return (
    <select
      className={cn(
        "h-10 rounded-md border border-border bg-input px-3 text-sm text-foreground outline-none focus:border-primary focus:ring-[3px] focus:ring-primary/10",
        className,
      )}
      {...props}
    />
  );
}

export function Panel({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card p-5 shadow-e1 transition-colors",
        className,
      )}
      {...props}
    />
  );
}

export function MetricCard({
  icon: Icon,
  title,
  value,
  trend,
  sub,
  data,
}: {
  icon: ElementType;
  title: string;
  value: string;
  trend?: number;
  sub?: string;
  data?: { v: number }[];
}) {
  const up = (trend ?? 0) >= 0;
  return (
    <Panel className="hover:border-primary hover:shadow-e2">
      <div className="flex items-start justify-between">
        <div className="grid size-10 place-items-center rounded-md bg-primary/15 text-primary">
          <Icon className="size-5" />
        </div>
        {trend !== undefined && (
          <span
            className={cn(
              "inline-flex items-center gap-1 text-[12px] font-semibold",
              up ? "text-primary" : "text-destructive",
            )}
          >
            {up ? <TrendingUp className="size-3.5" /> : <TrendingDown className="size-3.5" />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <p className="mt-4 text-sm font-medium text-muted-foreground">{title}</p>
      <div className="flex items-end justify-between gap-3">
        <p className="text-[28px] leading-tight font-bold text-primary">{value}</p>
        {data && (
          <div className="h-[28px] w-[84px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <Area
                  type="monotone"
                  dataKey="v"
                  stroke="var(--color-primary)"
                  fill="var(--color-primary)"
                  fillOpacity={0.2}
                  strokeWidth={1.5}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
      {sub && <p className="mt-1 text-[12px] text-muted-foreground">{sub}</p>}
    </Panel>
  );
}

export function TableShell({ children, toolbar }: { children: ReactNode; toolbar?: ReactNode }) {
  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card shadow-e1">
      {toolbar && (
        <div className="flex flex-wrap items-center gap-3 border-b border-border p-4">
          {toolbar}
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">{children}</table>
      </div>
    </div>
  );
}

export function Th({ className, ...props }: ComponentProps<"th">) {
  return (
    <th
      className={cn(
        "label-xs border-b border-border bg-card px-4 py-3 whitespace-nowrap text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}

export function Td({ className, ...props }: ComponentProps<"td">) {
  return (
    <td className={cn("h-[52px] border-b border-border px-4 py-3 align-middle", className)} {...props} />
  );
}

export function Tr({ className, ...props }: ComponentProps<"tr">) {
  return (
    <tr
      className={cn(
        "border-l-4 border-transparent transition-colors duration-150 hover:bg-surface-hover",
        className,
      )}
      {...props}
    />
  );
}

export function Pager({ total, shown = 50 }: { total: number; shown?: number }) {
  const pages = Math.max(1, Math.ceil(total / shown));
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border p-4 text-[12px] text-muted-foreground">
      <span>
        Showing 1–{Math.min(shown, total)} of {total} results
      </span>
      <div className="flex items-center gap-2">
        <button
          disabled
          className="grid size-8 place-items-center rounded-md border border-border disabled:opacity-50"
          aria-label="Previous page"
        >
          <ChevronLeft className="size-4" />
        </button>
        {Array.from({ length: Math.min(pages, 5) }, (_, i) => (
          <button
            key={i}
            className={cn(
              "size-8 rounded-md border border-border font-semibold transition-colors",
              i === 0
                ? "border-primary bg-primary text-primary-foreground"
                : "hover:bg-surface-hover",
            )}
          >
            {i + 1}
          </button>
        ))}
        <button
          className="grid size-8 place-items-center rounded-md border border-border hover:bg-surface-hover"
          aria-label="Next page"
        >
          <ChevronRight className="size-4" />
        </button>
      </div>
    </div>
  );
}
