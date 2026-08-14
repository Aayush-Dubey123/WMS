import { cn } from "@/lib/utils";

const map: Record<string, string> = {
  PENDING: "bg-secondary text-foreground",
  ACTIVE: "bg-primary/20 text-primary",
  RESERVED: "bg-info/20 text-info",
  INSPECTED: "bg-info/20 text-info",
  STORED: "bg-primary/20 text-primary",
  PICKED: "bg-info/20 text-info",
  PACKED: "bg-warning/20 text-warning",
  SHIPPED: "bg-primary/20 text-primary",
  ERROR: "bg-destructive/20 text-destructive",
  INACTIVE: "bg-secondary text-muted-foreground",
  OWNER: "bg-primary/20 text-primary",
  MANAGER: "bg-info/20 text-info",
  STAFF: "bg-secondary text-secondary-foreground",
  // Ticket lifecycle (TicketStatus enum)
  ANNOUNCED: "bg-secondary text-foreground",
  ACCEPTED: "bg-info/20 text-info",
  ARRIVED: "bg-info/20 text-info",
  PENDING_INSPECTION: "bg-warning/20 text-warning",
  SHIPMENT_ARRIVED: "bg-info/20 text-info",
  PENDING_APPROVAL: "bg-warning/20 text-warning",
  SOLD: "bg-primary/20 text-primary",
  DECLINED: "bg-destructive/20 text-destructive",
  NEEDS_SPEC: "bg-warning/20 text-warning",
  DAMAGED: "bg-destructive/20 text-destructive",
  // Order lifecycle (OrderStatus enum)
  CANCELLED: "bg-destructive/20 text-destructive",
};

export function StatusBadge({ status, className }: { status: string; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-[20px] px-3 py-1 text-[12px] font-semibold tracking-[0.3px]",
        map[status] ?? "bg-secondary text-foreground",
        className,
      )}
    >
      {status}
    </span>
  );
}
