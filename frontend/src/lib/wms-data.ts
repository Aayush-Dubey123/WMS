export type OrderStatus = "PENDING" | "RESERVED" | "PACKED" | "SHIPPED" | "ERROR";
export type TicketStatus = "PENDING" | "INSPECTED" | "STORED" | "PICKED";

export type Order = {
  id: string;
  customer: string;
  email: string;
  phone: string;
  warehouse: string;
  status: OrderStatus;
  created: string;
  items: { sku: string; product: string; qty: number; price: number }[];
};

export type Ticket = {
  id: string;
  warehouse: string;
  status: TicketStatus;
  arrived: string;
  storage: string;
  manager: string;
  carrier: string;
  tracking: string;
  noTicket: boolean;
  items: {
    barcode: string;
    product: string;
    qty: number;
    dims: string;
    weight: string;
    damaged: boolean;
    storage: string;
    status: string;
  }[];
};

const products = [
  ["WGT-1001", "Widget A — Steel Bracket", 24.5],
  ["WGT-1042", "Widget B — Nylon Sleeve", 8.25],
  ["PLT-3390", "Pallet Wrap 18in", 42.0],
  ["BOX-2210", "Corrugated Box 12x12", 1.85],
  ["SNS-8801", "Thermal Sensor Module", 128.4],
] as const;

const customers = [
  "Northline Supply Co.",
  "Harper & Vale Retail",
  "Kestrel Logistics",
  "Bluepoint Industrial",
  "Orchard Grove Foods",
  "Marlow Hardware",
  "Vertex Components",
  "Sable Freight Group",
];

const warehouses = ["WHT-01 · Whitfield North", "WHT-02 · Dalton Yard", "WHT-03 · Redmoor"];
const statuses: OrderStatus[] = ["PENDING", "RESERVED", "PACKED", "SHIPPED", "ERROR"];

export const orders: Order[] = Array.from({ length: 42 }, (_, i) => {
  const n = 1001 + i;
  const items = Array.from({ length: (i % 3) + 1 }, (_, j) => {
    const p = products[(i + j) % products.length]!;
    return { sku: p[0], product: p[1], qty: ((i + j) % 5) + 1, price: p[2] };
  });
  return {
    id: `ORD-${n}`,
    customer: customers[i % customers.length]!,
    email: `ops@${customers[i % customers.length]!.split(" ")[0]!.toLowerCase()}.com`,
    phone: `+1 (415) 555-0${(100 + i).toString().slice(0, 3)}`,
    warehouse: warehouses[i % warehouses.length]!,
    status: statuses[i % (i % 7 === 0 ? 5 : 4)]!,
    created: `Aug ${((i % 12) + 1).toString().padStart(2, "0")}, 2026 · ${(8 + (i % 9)).toString().padStart(2, "0")}:${(i % 6) * 10 || "05"}`,
    items,
  };
});

export const orderTotal = (o: Order) =>
  o.items.reduce((sum, it) => sum + it.qty * it.price, 0);

const ticketStatuses: TicketStatus[] = ["PENDING", "INSPECTED", "STORED", "PICKED"];

export const tickets: Ticket[] = Array.from({ length: 24 }, (_, i) => ({
  id: `RNO-20260813-${(i + 1).toString().padStart(3, "0")}`,
  warehouse: warehouses[i % warehouses.length]!,
  status: ticketStatuses[i % ticketStatuses.length]!,
  arrived: `Aug ${((i % 13) + 1).toString().padStart(2, "0")}, 2026 · ${(7 + (i % 10)).toString().padStart(2, "0")}:15`,
  storage: `A-${((i % 9) + 1).toString().padStart(2, "0")}-${((i * 3) % 40).toString().padStart(2, "0")}`,
  manager: ["John Mercer", "Ada Sloane", "Ravi Menon"][i % 3]!,
  carrier: ["FedEx Freight", "UPS Ground", "Estes Express"][i % 3]!,
  tracking: `1Z9${(884213 + i * 977).toString()}US`,
  noTicket: i % 5 === 0,
  items: Array.from({ length: (i % 4) + 2 }, (_, j) => {
    const p = products[(i + j) % products.length]!;
    return {
      barcode: `0123456789${((i + j) % 10).toString()}5`,
      product: p[1],
      qty: ((i + j) % 8) + 1,
      dims: `${8 + j}in x ${5 + j}in`,
      weight: `${(2.5 + j).toFixed(1)} lbs`,
      damaged: (i + j) % 7 === 0,
      storage: `A-${((i % 9) + 1).toString().padStart(2, "0")}-${((i + j) % 40).toString().padStart(2, "0")}`,
      status: ["SCANNED", "INSPECTED", "STORED"][(i + j) % 3]!,
    };
  }),
}));

export const users = Array.from({ length: 14 }, (_, i) => ({
  name: [
    "John Mercer",
    "Ada Sloane",
    "Ravi Menon",
    "Grace Okoye",
    "Tom Alvarez",
    "Lena Fischer",
    "Sam Whitfield",
  ][i % 7]!,
  email: `user${i + 1}@whitfieldwms.com`,
  role: (["OWNER", "MANAGER", "STAFF"] as const)[i % 3 === 0 && i < 3 ? 0 : i % 2 === 0 ? 1 : 2],
  warehouse: warehouses[i % warehouses.length]!,
  active: i % 6 !== 0,
  created: `Aug ${((i % 20) + 1).toString().padStart(2, "0")}, 2026`,
}));

export const warehouseList = [
  {
    code: "WHT-01",
    name: "Whitfield North",
    address: "1420 Harbor Rd, Oakland, CA 94607",
    manager: "John Mercer",
    tickets: 45,
    items: 2310,
    utilization: 85,
    active: true,
  },
  {
    code: "WHT-02",
    name: "Dalton Yard",
    address: "88 Dalton Ave, Reno, NV 89502",
    manager: "Ada Sloane",
    tickets: 28,
    items: 1408,
    utilization: 62,
    active: true,
  },
  {
    code: "WHT-03",
    name: "Redmoor",
    address: "7 Redmoor Industrial Park, Boise, ID 83702",
    manager: "Ravi Menon",
    tickets: 12,
    items: 640,
    utilization: 34,
    active: false,
  },
];

export const stockRows = products.map((p, i) => ({
  sku: p[0],
  product: p[1],
  warehouse: warehouseList[i % 3]!.code,
  onHand: 400 - i * 47,
  available: 320 - i * 41,
  reserved: 60 + i * 5,
  damaged: i * 3,
  modified: `Aug 1${i}, 2026 · 14:2${i}`,
}));

export const activity = [
  { time: "14:32", type: "ORDER_SHIPPED", actor: "Ada Sloane", ref: "ORD-1032", status: "SHIPPED" },
  { time: "14:11", type: "TICKET_STORED", actor: "Ravi Menon", ref: "RNO-20260813-004", status: "STORED" },
  { time: "13:58", type: "ORDER_PACKED", actor: "Tom Alvarez", ref: "ORD-1029", status: "PACKED" },
  { time: "13:40", type: "ITEM_DAMAGED", actor: "Grace Okoye", ref: "RNO-20260813-002", status: "ERROR" },
  { time: "13:12", type: "STOCK_RESERVED", actor: "System", ref: "ORD-1027", status: "RESERVED" },
  { time: "12:47", type: "ARRIVAL_LOGGED", actor: "John Mercer", ref: "RNO-20260813-006", status: "PENDING" },
  { time: "12:20", type: "USER_CREATED", actor: "Sam Whitfield", ref: "lena.f@…", status: "ACTIVE" },
  { time: "11:58", type: "ORDER_CREATED", actor: "Kestrel Logistics", ref: "ORD-1041", status: "PENDING" },
  { time: "11:22", type: "TICKET_INSPECTED", actor: "Ada Sloane", ref: "RNO-20260813-009", status: "INSPECTED" },
  { time: "10:44", type: "ORDER_SHIPPED", actor: "Ravi Menon", ref: "ORD-1018", status: "SHIPPED" },
];

export const statusDonut = [
  { name: "Pending", value: 42, color: "#9CA3AF" },
  { name: "Reserved", value: 31, color: "#3B82F6" },
  { name: "Packed", value: 26, color: "#F59E0B" },
  { name: "Shipped", value: 88, color: "#10B981" },
];

export const warehouseBars = [
  { name: "WHT-01", orders: 132 },
  { name: "WHT-02", orders: 88 },
  { name: "WHT-03", orders: 41 },
];

export const trendData = Array.from({ length: 12 }, (_, i) => ({
  day: `${i + 1}`,
  orders: 40 + Math.round(Math.sin(i / 2) * 18) + i * 2,
  arrivals: 22 + Math.round(Math.cos(i / 2) * 10) + i,
}));

export const spark = (seed: number) =>
  Array.from({ length: 12 }, (_, i) => ({
    v: 20 + Math.round(Math.sin((i + seed) / 1.7) * 8) + i,
  }));
