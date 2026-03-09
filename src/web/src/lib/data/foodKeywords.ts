/** Static mapping of food names to display info and categories. */

export interface FoodInfo {
  name: string;
  icon: string;
  category: "fruit" | "dairy" | "beverage" | "alcohol" | "meal" | "other";
  categoryLabel: string;
}

export const FOOD_KEYWORDS: Record<string, FoodInfo> = {
  "\uC790\uBABD": { name: "\uC790\uBABD", icon: "\uD83C\uDF4A", category: "fruit", categoryLabel: "\uACFC\uC77C" },
  "\uC790\uBABD\uC8FC\uC2A4": { name: "\uC790\uBABD\uC8FC\uC2A4", icon: "\uD83E\uDDC3", category: "fruit", categoryLabel: "\uACFC\uC77C" },
  "\uC6B0\uC720": { name: "\uC6B0\uC720", icon: "\uD83E\uDD5B", category: "dairy", categoryLabel: "\uC720\uC81C\uD488" },
  "\uC720\uC81C\uD488": { name: "\uC720\uC81C\uD488", icon: "\uD83E\uDDC0", category: "dairy", categoryLabel: "\uC720\uC81C\uD488" },
  "\uCE58\uC988": { name: "\uCE58\uC988", icon: "\uD83E\uDDC0", category: "dairy", categoryLabel: "\uC720\uC81C\uD488" },
  "\uC694\uAD6C\uB974\uD2B8": { name: "\uC694\uAD6C\uB974\uD2B8", icon: "\uD83E\uDD5B", category: "dairy", categoryLabel: "\uC720\uC81C\uD488" },
  "\uC54C\uCF54\uC62C": { name: "\uC54C\uCF54\uC62C", icon: "\uD83C\uDF7A", category: "alcohol", categoryLabel: "\uC8FC\uB958" },
  "\uC74C\uC8FC": { name: "\uC74C\uC8FC", icon: "\uD83C\uDF7A", category: "alcohol", categoryLabel: "\uC8FC\uB958" },
  "\uC8FC\uB958": { name: "\uC8FC\uB958", icon: "\uD83C\uDF7E", category: "alcohol", categoryLabel: "\uC8FC\uB958" },
  "\uC220": { name: "\uC220", icon: "\uD83C\uDF76", category: "alcohol", categoryLabel: "\uC8FC\uB958" },
  "\uCE74\uD398\uC778": { name: "\uCE74\uD398\uC778", icon: "\u2615", category: "beverage", categoryLabel: "\uC74C\uB8CC" },
  "\uCEE4\uD53C": { name: "\uCEE4\uD53C", icon: "\u2615", category: "beverage", categoryLabel: "\uC74C\uB8CC" },
  "\uB179\uCC28": { name: "\uB165\uCC28", icon: "\uD83C\uDF75", category: "beverage", categoryLabel: "\uC74C\uB8CC" },
  "\uCC28": { name: "\uCC28", icon: "\uD83C\uDF75", category: "beverage", categoryLabel: "\uC74C\uB8CC" },
  "\uC2DD\uC0AC": { name: "\uC2DD\uC0AC", icon: "\uD83C\uDF5A", category: "meal", categoryLabel: "\uC2DD\uC0AC" },
  "\uC74C\uC2DD": { name: "\uC74C\uC2DD", icon: "\uD83C\uDF5C", category: "meal", categoryLabel: "\uC2DD\uC0AC" },
  "\uACFC\uC77C": { name: "\uACFC\uC77C", icon: "\uD83C\uDF4E", category: "fruit", categoryLabel: "\uACFC\uC77C" },
  "\uBC14\uB098\uB098": { name: "\uBC14\uB098\uB098", icon: "\uD83C\uDF4C", category: "fruit", categoryLabel: "\uACFC\uC77C" },
  "\uC624\uB80C\uC9C0": { name: "\uC624\uB80C\uC9C0", icon: "\uD83C\uDF4A", category: "fruit", categoryLabel: "\uACFC\uC77C" },
  "\uCE7C\uC290": { name: "\uCE7C\uC290", icon: "\uD83E\uDD5B", category: "dairy", categoryLabel: "\uC720\uC81C\uD488" },
  "\uCCA0\uBD84": { name: "\uCCA0\uBD84", icon: "\uD83E\uDDCA", category: "other", categoryLabel: "\uAE30\uD0C0" },
  "\uBE44\uD0C0\uBBFC K": { name: "\uBE44\uD0C0\uBBFC K", icon: "\uD83E\uDD66", category: "other", categoryLabel: "\uAE30\uD0C0" },
  "\uC2DC\uAE08\uCE58": { name: "\uC2DC\uAE08\uCE58", icon: "\uD83E\uDD6C", category: "other", categoryLabel: "\uAE30\uD0C0" },
  "\uBE0C\uB85C\uCF5C\uB9AC": { name: "\uBE0C\uB85C\uCF5C\uB9AC", icon: "\uD83E\uDD66", category: "other", categoryLabel: "\uAE30\uD0C0" },
  "\uACE0\uC9C0\uBC29": { name: "\uACE0\uC9C0\uBC29 \uC2DD\uC0AC", icon: "\uD83C\uDF54", category: "meal", categoryLabel: "\uC2DD\uC0AC" },
  "\uC778\uC0BC": { name: "\uC778\uC0BC", icon: "\uD83C\uDF3F", category: "other", categoryLabel: "\uAE30\uD0C0" },
  "\uB9C8\uB298": { name: "\uB9C8\uB298", icon: "\uD83E\uDDC4", category: "other", categoryLabel: "\uAE30\uD0C0" },
};

/** All food keyword strings for matching. */
export const FOOD_KEYWORD_LIST = Object.keys(FOOD_KEYWORDS);
