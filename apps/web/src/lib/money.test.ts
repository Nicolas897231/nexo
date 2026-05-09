import { describe, expect, it } from "vitest";
import { formatMoney, isValidMoneyString, normalizeMoney } from "@/lib/money";

describe("money helpers", () => {
  it("normalizes displayed money to string decimal without using float as source", () => {
    expect(normalizeMoney("$1.600.000")).toBe("1600000.00");
    expect(normalizeMoney("$160.000.000")).toBe("160000000.00");
    expect(normalizeMoney("$1.600.000,50")).toBe("1600000.50");
  });

  it("validates money strings before sending to backend", () => {
    expect(isValidMoneyString("1600000.00")).toBe(true);
    expect(isValidMoneyString("-1.00")).toBe(false);
    expect(isValidMoneyString("abc")).toBe(false);
    expect(isValidMoneyString("0.00")).toBe(false);
    expect(isValidMoneyString("0.00", { allowZero: true })).toBe(true);
  });

  it("formats values for Colombian users", () => {
    expect(formatMoney("1600000.00")).toContain("1.600.000");
  });
});
