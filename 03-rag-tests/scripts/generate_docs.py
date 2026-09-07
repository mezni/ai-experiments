"""
Knowledge Base Data Generator — Aether Wireless
=================================================
Generates Category B knowledge base documents (policies, processes,
eligibility terms, terms & conditions) for the Aether Wireless
telecom retail domain.

Each curated document carries its canonical metadata (title, Document ID,
version, last-updated date, department) and body text inline.

Output is written to:
    data/policies/<policy_name>.md

    - billing_invoice_policy.md
    - data_plan_terms_conditions.md
    - device_protection_policy.md
    - device_trade_in_process.md
    - device_upgrade_guidelines.md
    - international_roaming_policy.md
    - loyalty_rewards_program.md
    - new_line_activation_process.md
    - network_service_level_agreement.md
    - payment_eligibility_terms.md
    - plan_upgrade_policy.md
    - port_in_policy.md
    - postpaid_plan_guidelines.md
    - privacy_data_protection_policy.md
    - promotions_eligibility_terms.md
    - returns_refunds_policy.md

Std-lib only. Run:  python scripts/generate_docs.py
"""

from dataclasses import dataclass
from pathlib import Path

# ==============================================================================
# 0. OUTPUT PATH
# ==============================================================================

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "data" / "policies"

# ==============================================================================
# 1. KNOWLEDGE DOCUMENT SCHEMA
# ==============================================================================


@dataclass
class KnowledgeMetadata:
    title: str
    doc_id: str
    version: str
    last_updated: str
    department: str


@dataclass
class KnowledgeDocument:
    metadata: KnowledgeMetadata
    body: str

    @property
    def rendered(self) -> str:
        m = self.metadata
        header = (
            f"# {m.title}\n\n"
            f"## Document Information\n"
            f"- **Document ID:** {m.doc_id}\n"
            f"- **Version:** {m.version}\n"
            f"- **Last Updated:** {m.last_updated}\n"
            f"- **Department:** {m.department}\n"
            f"- **Company:** Aether Wireless\n\n"
            f"---\n\n"
        )
        return header + self.body.strip() + "\n"


# ==============================================================================
# 2. CURATED KNOWLEDGE DOCUMENTS (canonical metadata + curated body text)
#     Company: Aether Wireless
# ==============================================================================

KB = {

    # -------------------------------------------------------------------------
    # B.1  Postpaid Plan Guidelines
    # -------------------------------------------------------------------------
    "postpaid_plan_guidelines.md": {
        "metadata": KnowledgeMetadata(
            title="Postpaid Plan Guidelines",
            doc_id="AW-PLN-001",
            version="3.0",
            last_updated="August 2026",
            department="Consumer Plans",
        ),
        "body": """## Overview

Aether Wireless offers tiered postpaid plans for individual and family lines. This document covers plan categories, allowances, overage behavior, and feature availability per plan.

## Plan Categories

### 1. Essential
- Entry-level plan for light users.
- 5 GB high-speed data, 500 talk minutes, 500 SMS.
- Monthly price: $40/month.
- No hotspot, no international calling.
- Ideal for seniors and secondary lines.

### 2. Standard
- Mid-tier plan for everyday users.
- 20 GB high-speed data, 1,000 talk minutes, 1,000 SMS.
- Monthly price: $60/month.
- Mobile hotspot included (10 GB/month).
- Wi-Fi calling supported.

### 3. Premium
- High-tier plan for heavy users.
- 50 GB high-speed data, unlimited talk & text.
- Monthly price: $80/month.
- 25 GB hotspot, international calling to 50+ countries included.
- Priority network access during congestion.

### 4. Family
- Multi-line plan for households (2+ lines).
- 100 GB shared data pool, unlimited talk & text.
- Monthly price: $120/month (includes 2 lines; +$30/line).
- Data prioritization: Primary line gets 60% of shared pool.
- Requires at least two lines on the account.

### 5. Unlimited
- Truly unlimited high-speed data, talk, and text.
- Monthly price: $90/month.
- 50 GB hotspot, international calling to 80+ countries.
- Network deprioritization only during extreme congestion.

### 6. Business
- Enterprise plan with SLA guarantees.
- 200 GB pooled data per 5 lines, unlimited talk & text.
- Monthly price: $200/month (5 lines; +$40/line).
- Dedicated business support line, MDM-ready.

### 7. Senior
- Discounted plan for customers 65+.
- 10 GB high-speed data, unlimited talk & text.
- Monthly price: $30/month.
- No hotspot, domestic calling only.
- Requires age verification at activation.

---

## Data Allowance Behavior

| Plan        | High-Speed Data       | After Allowance                                     |
|-------------|-----------------------|-----------------------------------------------------|
| Essential   | 5 GB                  | Throttled to 128 kbps                               |
| Standard    | 20 GB                 | Throttled to 256 kbps                               |
| Premium     | 50 GB                 | Throttled to 512 kbps                               |
| Family      | 100 GB shared         | Throttled to 256 kbps per line                      |
| Unlimited   | Unlimited             | Priority below Essential users during congestion    |
| Business    | 200 GB pooled         | Throttled to 1 Mbps per line                        |
| Senior      | 10 GB                 | Throttled to 128 kbps                               |

**Overage:** No hard data caps on Premium, Family, Unlimited, or Business plans. Essential, Standard, and Senior deprioritize instead of overage billing.

---

## Plan Features Matrix

| Feature            | Essential | Standard | Premium | Family | Unlimited | Business | Senior |
|--------------------|-----------|----------|---------|--------|-----------|----------|--------|
| Talk (min)         | 500       | 1,000    | Unlimited| Unlimited| Unlimited| Unlimited| Unlimited|
| Text               | 500       | 1,000    | Unlimited| Unlimited| Unlimited| Unlimited| Unlimited|
| Hotspot            | No        | 10 GB    | 25 GB   | 10 GB  | 50 GB     | Yes      | No     |
| Intl. Calling      | No        | No       | 50+ ctry| No     | 80+ ctry  | Yes      | No     |
| Wi-Fi Calling      | No        | Yes      | Yes     | Yes    | Yes       | Yes      | Yes    |
| Priority Network   | No        | No       | Yes     | No     | Yes       | Yes      | No     |
| Mobile Hotspot     | No        | Shared   | Dedicated| Shared| Dedicated | Shared   | No     |
| Voicemail          | No        | Yes      | Yes     | Yes    | Yes       | Yes      | Yes    |
| Call Forwarding    | No        | Yes      | Yes     | Yes    | Yes       | Yes      | No     |
| Spam Call Blocking | No        | Yes      | Yes     | Yes    | Yes       | Yes      | Yes    |

---

## Change Policies

- **Downgrade:** Effective from next billing cycle.
- **Upgrade:** Effective immediately; prorated charges apply.
- **Mid-cycle changes:** Full plan price billed on change date.
- 14-day cooling-off period for new lines (see Returns & Refunds Policy).
- Plan changes do not affect device installment contracts.

---

## Promotional Pricing

- Promotions are per-account, not per-line.
- A maximum of two promotional discounts may apply simultaneously.
- Promotional prices return to standard rates at the end of the promo period.
- Customers are notified 30 days before promo expiry.

---

## FAQs

**Q: Can I share my data with other lines?**
A: On Family plans, data is automatically shared. Other plans can add data sharing for $10/month.

**Q: What happens when I travel abroad?**
A: Premium, Family, Unlimited, and Business plans include international calling. Essential and Standard require a travel add-on ($15/day for 500 MB + unlimited calls in destination).

**Q: Can I switch plans at any time?**
A: Yes, subject to plan activation dates and proration rules above.

**Q: Is there a family discount?**
A: Yes, the Family plan saves approximately 25% vs. two Standard plans.

**Q: Do unused data roll over?**
A: No. Data allowances reset each billing cycle.

---

**Contact Plan Team:**
- Plan Helpline: 1-833-AETHER
- Email: plans@aetherwireless.com
- Visit nearest Aether Wireless retail store

*Plans and pricing subject to change. Terms and conditions apply.*""",
    },

    # -------------------------------------------------------------------------
    # B.2  Plan Upgrade Policy
    # -------------------------------------------------------------------------
    "plan_upgrade_policy.md": {
        "metadata": KnowledgeMetadata(
            title="Plan Upgrade Policy",
            doc_id="AW-PLN-002",
            version="2.0",
            last_updated="July 2026",
            department="Consumer Plans",
        ),
        "body": """## Overview

This policy defines when and how a customer may move to a higher-tier plan, how eligibility is determined, and how promotional pricing applies during upgrades.

## Eligibility Criteria

A customer is eligible for an immediate plan upgrade when:

- Account is in **Active** status (no outstanding balance older than 30 days).
- Current plan has been on the account for at least **30 days**.
- No unpaid device installment balance in arrears.
- Identity verification is current (KYC within last 12 months).
- Customer is not flagged for fraud or abuse review.

**Exclusions:**
- Accounts flagged for fraud or abuse.
- Delinquent accounts (balance outstanding > 30 days).
- Accounts under credit review.

---

## Account Status Rules

| Account Status | Upgrade Allowed | Notes |
|----------------|-----------------|-------|
| Active         | Yes             | Immediate processing |
| Prospect       | Yes             | Requires new plan activation first |
| Delinquent     | No              | Must settle balance, then upgrade |
| Suspended      | No              | Must contact Customer Care |

---

## Available Upgrade Paths

| Current Plan | Available Upgrades | Minimum Tenure |
|--------------|--------------------|----------------|
| Essential    | Standard, Premium, Family | 30 days |
| Standard     | Premium, Family, Unlimited | 30 days |
| Premium      | Unlimited, Family, Business | 30 days |
| Family       | Unlimited, Business | 30 days |
| Senior       | Essential, Standard, Premium | 60 days |

**Note:** Business plan requires a minimum of 5 lines and credit approval.

---

## Upgrade Process

1. Representative confirms eligibility (see criteria above).
2. System analyzes 60-day average data/talk usage to recommend target plan.
3. Representative presents recommendation and alternative tiers.
4. Customer consents to new plan price and effective date.
5. Any applicable promotion is applied (e.g., PROMO-0001 Premium Upgrade Discount).
6. System applies change; customer receives confirmation SMS within 5 minutes.
7. Updated terms are emailed to customer within 24 hours.

---

## Proration Rules

- Upgrades take effect **immediately** on the change date.
- The customer pays the difference between old and new monthly price for the remainder of the cycle.
- Prorated amount is calculated as: `(new_price - old_price) × days_remaining / days_in_cycle`.
- Device installment schedules are unaffected by plan changes.
- Taxes and regulatory fees are recalculated on the new plan price.

---

## Promotional Pricing

- Promotions stack only if explicitly stated (e.g., bundle offers).
- Discount duration is noted at offer time; plan returns to standard price after expiry.
- Representative must inform customer of the post-promotion price.
- Customers may opt out of a promotion within 30 days without penalty.

---

## Usage-Based Recommendations

The Aether Wireless system performs automated plan reviews:

- **Downgrade candidates:** Usage < 40% of plan allowance for 3 consecutive months.
- **Upgrade candidates:** Usage > 80% of plan allowance for 2 consecutive months.
- Recommendations are sent via SMS at the start of each billing cycle.
- Customers may request a usage review at any time.

---

## FAQs

**Q: How soon can I upgrade after joining?**
A: Typically 30 days after activation, or earlier during promotional windows.

**Q: Do I lose my number when I upgrade?**
A: No. Number portability is independent of plan changes.

**Q: Can I upgrade a single line on a Family plan?**
A: No. Family plans change as a unit; per-line add-ons are available instead.

**Q: Will my hotspot allowance increase?**
A: Yes, the new plan's hotspot allowance applies immediately.

**Q: Can I reverse an upgrade?**
A: Within 24 hours, a reversal can be processed by Customer Care. After 24 hours, the change is effective until the next billing cycle.

---

**Contact Plan Team:**
- Plan Helpline: 1-833-AETHER
- Email: plans@aetherwireless.com

*Terms and conditions apply.*""",
    },

    # -------------------------------------------------------------------------
    # B.3  Data Plan Terms & Conditions
    # -------------------------------------------------------------------------
    "data_plan_terms_conditions.md": {
        "metadata": KnowledgeMetadata(
            title="Data Plan Terms & Conditions",
            doc_id="AW-PLN-003",
            version="3.1",
            last_updated="June 2026",
            department="Legal & Compliance",
        ),
        "body": """## Overview

These terms govern all data allowances, speeds, add-ons, and network management policies across all Aether Wireless postpaid and prepaid plans. They form part of the subscriber agreement.

## Fair Usage Policy

- Data allowances are for personal, non-commercial use.
- Unlimited plans are subject to network management during congestion.
- Automated downloading, torrenting beyond stated limits, tethering beyond plan allowances, and reselling are prohibited.
- Aether Wireless reserves the right to throttle or suspend accounts engaged in abusive usage.

---

## Speed & Throttling

| Condition | Result |
|-----------|--------|
| Allowance exhausted (Essential/Standard) | Throttled to 128 kbps / 256 kbps respectively |
| Allowance exhausted (Premium/Unlimited) | Throttled to 512 kbps |
| Congestion (Unlimited) | Prioritized below postpaid Essentials |
| International roaming data | Speed reduced to 3G/4G as per destination network |
| Tethering beyond hotspot allowance | Throttled to 64 kbps |
| Business plan | Throttled to 1 Mbps after 200 GB |

---

## Data Add-ons

- **Data Boost 1 GB:** $10 — valid for current billing cycle.
- **Data Boost 5 GB:** $35 — valid for current billing cycle.
- **International Roaming Pass:** $15/day — 500 MB + unlimited calls in destination.
- **Tethering Boost 10 GB:** $12 — for Essential and Standard plans.
- Add-on data does not roll over to the next cycle.
- Add-on charges are billed in the next invoice.
- Customers can purchase add-ons via app, website, or in-store.

---

## Roaming Data Terms

- Roaming is available in 180+ countries.
- Speeds depend on partner network availability.
- Data roaming is disabled by default; must be enabled in account settings.
- Roaming charges apply at published rates unless a Roaming Pass is active.

---

## Bill Optimization Guidance

Customers seeking to reduce monthly bills should consider:

1. Moving to a lower tier if 60-day average usage < 60% of allowance.
2. Enabling autopay for a $5/month recurring discount.
3. Consolidating multiple lines onto a Family plan.
4. Using Wi-Fi calling to reduce talk-minute usage.
5. Removing unused add-ons from the account.

---

## Compliance Notes

- All terms are part of the Aether Wireless subscriber agreement.
- Changes to terms require 30 days written notice.
- Customers may terminate without penalty upon material term changes.
- Aether Wireless complies with FCC network management disclosure requirements.

---

## Dispute Resolution

- Data quality complaints must be reported within 30 days.
- Aether Wireless investigates within 5 business days.
- Credits are issued for verified network quality issues.
- Customers may escalate to the FCC if unresolved after 60 days.

---

**Contact Legal:**
- Email: legal@aetherwireless.com
- Regulatory Affairs: regulatory@aetherwireless.com

*Terms subject to regulatory change.*""",
    },

    # -------------------------------------------------------------------------
    # B.4  Device Upgrade Guidelines
    # -------------------------------------------------------------------------
    "device_upgrade_guidelines.md": {
        "metadata": KnowledgeMetadata(
            title="Device Upgrade Guidelines",
            doc_id="AW-DEV-001",
            version="2.0",
            last_updated="August 2026",
            department="Device Finance",
        ),
        "body": """## Overview

Device upgrades allow customers to move to a newer handset, typically with trade-in credit, installment financing, or promotional pricing. This document covers eligibility, timing, financing options, and the upgrade workflow.

## Upgrade Eligibility

- Device must be on the account for at least **12 months** (or 50% of installment term).
- No more than **2 unpaid installments** on the current device.
- Account status: Active (see Plan Upgrade Policy for status rules).
- Customer must not have exceeded device financing limits (see below).

### Device Financing Limits

| Credit Tier | Max Devices Financed | Max Monthly Financing |
|-------------|----------------------|----------------------|
| Tier A (Excellent) | 4 | $200/month total |
| Tier B (Good) | 3 | $150/month total |
| Tier C (Fair) | 2 | $100/month total |

### Early Upgrade Options

| Situation | Option |
|-----------|--------|
| 12+ months on device | Standard upgrade with trade-in |
| Device damaged | Device protection claim, then upgrade |
| Device lost/stolen | Protection plan payout, then upgrade |
| < 12 months | Pay remaining balance, then upgrade |

---

## Available Devices

| Device | Retail Price | Term | Est. /month | Plan Required |
|--------|--------------|------|-------------|---------------|
| iPhone 16 | $899 | 24 mo | $37.46 | Essential+ |
| iPhone 16 Pro | $1,199 | 24 mo | $49.96 | Standard+ |
| Samsung Galaxy S25 | $899 | 24 mo | $37.46 | Essential+ |
| Samsung Galaxy S25 Ultra | $1,299 | 24 mo | $54.12 | Standard+ |
| Google Pixel 9 | $799 | 24 mo | $33.29 | Essential+ |
| Google Pixel 9 Pro | $999 | 24 mo | $41.63 | Standard+ |
| OnePlus 12 | $699 | 24 mo | $29.13 | Essential+ |
| Motorola Edge 50 | $599 | 24 mo | $24.96 | Essential+ |

- 0% APR when device is financed on a Premium, Unlimited, or Business plan.
- 6.99% APR on Essential and Standard plans.
- Down payment may be required for Tier C credit customers.

---

## Trade-In Value Estimates

See `device_trade_in_process.md` for the full trade-in procedure.

| Device Category | Age | Typical Value Range |
|-----------------|-----|---------------------|
| Flagship phones | < 2 years | 40–60% of original retail |
| Mid-range phones | < 3 years | 25–40% of original retail |
| Budget phones | < 2 years | 15–25% of original retail |
| Damaged devices | Any | 10–30% (screen cracks, water damage) |

---

## Upgrade Process

1. Confirm account status and installment eligibility.
2. System runs 60-day usage analysis to recommend target device.
3. Representative presents device options and financing terms.
4. Customer selects device; trade-in is processed if applicable.
5. New installment agreement is signed.
6. Device is activated in-store or shipped within 2 business days.
7. Old device is collected (in-store) or shipped via prepaid label (7-day window).
8. Customer receives activation confirmation SMS.

---

## Device Insurance During Upgrade

- Device protection transfers to the new device automatically.
- No gap in coverage between old and new device.
- Deductible amounts remain the same unless plan tier changes.

---

## FAQs

**Q: Can I pay off my device early?**
A: Yes, full balance can be paid at any time. Promotional credits may be forfeited if paid off before the promo term.

**Q: Can I transfer my device to another line?**
A: Yes, if both lines are on the same account.

**Q: Do I keep my old number on upgrade?**
A: Yes, number and plan remain unchanged.

**Q: What if my device is not in working condition?**
A: Trade-in value will be reduced. Consider filing a protection claim first.

**Q: Can I upgrade multiple lines at once?**
A: Yes, each line is evaluated independently.

---

**Contact Device Team:**
- Device Helpline: 1-833-AETHER-DEV
- Email: devices@aetherwireless.com

*Terms and conditions apply.*""",
    },

    # -------------------------------------------------------------------------
    # B.5  Device Trade-In Process
    # -------------------------------------------------------------------------
    "device_trade_in_process.md": {
        "metadata": KnowledgeMetadata(
            title="Device Trade-In Process",
            doc_id="AW-DEV-002",
            version="2.3",
            last_updated="July 2026",
            department="Device Finance",
        ),
        "body": """## Overview

The Aether Wireless trade-in program credits customers for their current device toward a new purchase. This process document details assessment, valuation, credit application, and device handling.

## Eligibility

- Original device must be owned by the account holder.
- Device must power on and hold a charge for valuation.
- Account must be Active (see Plan Upgrade Policy).
- Device must not be reported lost or stolen.

---

## Valuation Factors

| Factor | Influence |
|--------|-----------|
| Make & model | Base value table (updated quarterly) |
| Age | Depreciation over time (12–15% per year) |
| Screen condition | Cracks reduce value 30–50% |
| Battery health | < 80% capacity reduces value 10–20% |
| Activation lock | Must be removed before valuation |
| Water damage indicators | Reduces value 40–60% |
| Physical damage (frame, buttons) | Reduces value 15–30% |
| Accessories | Charger/box increase value by $10–20 |
| Software status | Jailbroken/rooted devices reduce value 20% |

---

## Valuation Tiers

| Tier | Condition | Description |
|------|-----------|-------------|
| A | Like New | No scratches, full battery, all accessories |
| B | Good | Minor wear, 80%+ battery, functional |
| C | Fair | Visible scratches, 70%+ battery, functional |
| D | Poor | Cracks, 60%+ battery, functional |
| E | Broken | Screen/non-functional, powers on |
| F | Non-functional | Does not power on |

---

## Trade-In Steps

1. Customer selects new device and opts into trade-in.
2. Representative runs device diagnostics (screen, battery, IMEI check).
3. System quotes trade-in value instantly based on valuation tier.
4. Customer accepts or declines the quote.
5. If accepted, trade-in credit is applied immediately to the new device purchase.
6. Old device is collected in-store or shipped via prepaid label (7-day window).
7. Device is sent to Aether Wireless refurbishment facility for final inspection.
8. If inspection confirms quoted condition, credit is finalized.
9. If condition differs from quote, customer is billed/credited the difference.

---

## Promotion Stacking

| Combination | Allowed |
|-------------|---------|
| Trade-in credit + Device promo (PROMO-0003) | Yes ($200 bonus) |
| Trade-in credit + Plan promo | Yes |
| Trade-in credit + Two device promos | No |
| Trade-in credit + Cash discount | Yes |

---

## Device Handling After Trade-In

- Devices in Tiers A–C are refurbished and resold.
- Devices in Tiers D–E are refurbished or recycled.
- Devices in Tier F are responsibly recycled.
- All data is wiped per NIST 800-88 standards.

---

## FAQs

**Q: Will I get a box to ship my phone?**
A: Yes, a prepaid shipping kit is provided in-store or by mail.

**Q: What if my phone has a cracked screen?**
A: It is still eligible; value is reduced to Tier D or E depending on damage.

**Q: When is my credit applied?**
A: Instantly at point of sale, subject to inspection confirmation.

**Q: Can I trade in a device without buying a new one?**
A: No, trade-in credits are applied toward a new device purchase only.

**Q: What happens to my data?**
A: Factory reset is recommended before trade-in. Aether Wireless performs NIST-compliant data wiping at the refurbishment facility.

---

**Contact Device Team:**
- Email: devices@aetherwireless.com

*Valuations subject to physical inspection. Values valid for 14 days from quote.*""",
    },

    # -------------------------------------------------------------------------
    # B.6  Device Protection Policy
    # -------------------------------------------------------------------------
    "device_protection_policy.md": {
        "metadata": KnowledgeMetadata(
            title="Device Protection Policy",
            doc_id="AW-DEV-003",
            version="2.0",
            last_updated="July 2026",
            department="Device Services",
        ),
        "body": """## Overview

Aether Wireless Device Protection covers accidental damage, loss, theft, and extended warranty. This policy describes plan tiers, coverage details, claims, and deductibles.

## Coverage Tiers

### Tier 1 — Screen Repair
- Front and rear screen replacement.
- Monthly cost: $5/month.
- Deductible: $29 per claim.
- Covers one screen repair per 12 months.

### Tier 2 — Full Protection
- Accidental damage (drops, spills).
- Liquid damage (submersion up to 30 minutes).
- Mechanical breakdown (after manufacturer warranty expires).
- Monthly cost: $12/month.
- Deductible: $99 per claim.
- Covers the full device value up to $1,500.

### Tier 3 — Loss & Theft
- Includes all Tier 2 coverage.
- Loss and theft replacement (device or cash payout).
- Monthly cost: $16/month.
- Deductible: $199 per claim.
- Replacement device ships within 24 hours; arrives in 1–3 business days.

### Tier 4 — Premium Care
- Includes all Tier 3 coverage.
- Deductible waived for first claim.
- $0 deductible for screen repairs.
- Covers accessories up to $200.
- Monthly cost: $22/month.

---

## Claim Process

1. Customer reports incident via app, website, or in-store.
2. Representative verifies coverage tier and account status.
3. Deductible is quoted and collected (if applicable).
4. Replacement device is authorized within 24 hours.
5. Replacement ships in 1–3 business days.
6. Customer has 14 days to return the damaged/lost device (if found).
7. Claim is closed upon receipt of replacement.

---

## Claim Limits

| Tier | Claims per 12 Months | Notes |
|------|---------------------|-------|
| Tier 1 (Screen) | 2 | Does not count against Tier 2/3 |
| Tier 2 (Full) | 2 | $99 deductible each |
| Tier 3 (Loss & Theft) | 2 | $199 deductible each |
| Tier 4 (Premium) | 3 | $0 first screen, $99 thereafter |

---

## Deductible Summary

| Tier | Screen | Accidental | Loss/Theft |
|------|--------|------------|------------|
| Tier 1 | $29 | N/A | N/A |
| Tier 2 | $99 | $99 | N/A |
| Tier 3 | $99 | $99 | $199 |
| Tier 4 | $0 | $99 | $199 |

---

## Activation & Cancellation

- Protection can be added within **30 days** of device purchase.
- Protection can be added or removed at any time during device ownership.
- Removal is effective at the end of the current billing cycle.
- Refund for the current month is not provided upon cancellation.

---

## Extended Manufacturer Warranty

- Tier 2+ includes an additional 12 months beyond manufacturer warranty.
- Covers mechanical breakdown only (not accidental damage).
- No additional deductible for warranty claims.

---

## Exclusions

- Cosmetic wear and tear (scratches, dents without functional damage).
- Devices purchased more than 30 days before coverage start (no retroactive coverage).
- Pre-existing damage at coverage purchase.
- Removal of activation lock cases.
- Loss/theft claims without a police report (required within 7 days).
- Devices not owned by the account holder.

---

## FAQs

**Q: Can I add protection after buying my phone?**
A: Yes, within 30 days of purchase.

**Q: What if my phone is lost while traveling?**
A: Loss & Theft tier covers worldwide; a police report is required.

**Q: How many claims can I file?**
A: Up to 2–3 per rolling 12 months depending on your tier.

**Q: Does my protection transfer if I upgrade?**
A: Yes, protection transfers to the new device automatically.

**Q: What if my replacement is refurbished?**
A: Aether Wireless provides like-new or certified refurbished devices. All replacements come with a 12-month warranty.

---

**Contact Device Services:**
- Protection Claims: 1-833-AETHER-CARE
- Email: protection@aetherwireless.com

*Deductibles and limits subject to change. See terms for full details.*""",
    },

    # -------------------------------------------------------------------------
    # B.7  Billing & Invoice Policy
    # -------------------------------------------------------------------------
    "billing_invoice_policy.md": {
        "metadata": KnowledgeMetadata(
            title="Billing & Invoice Policy",
            doc_id="AW-BIL-001",
            version="2.1",
            last_updated="August 2026",
            department="Finance Operations",
        ),
        "body": """## Overview

This policy governs how monthly invoices are generated, when autopay applies, how balances are treated, and the customer's rights regarding billing disputes.

## Invoice Cycle

- Invoices are issued monthly with a **15-day due window**.
- Invoice includes: plan charge, taxes & fees, add-ons, device installments, and any applicable credits.
- Invoices are available digitally (Aether Wireless app/portal) and sent by email.
- Paper invoices are available upon request ($2/month fee).

---

## Charges on Invoice

| Line Item | Description |
|-----------|-------------|
| Monthly Rate Plan | Base plan price (e.g., Standard $60) |
| Regulatory Taxes & Fees | Taxes and surcharges (~8–12% depending on jurisdiction) |
| Data / Talk Add-ons | One-time purchases |
| Device Installment | Monthly device payment |
| Protection Plan | Device protection monthly fee |
| Service Fees | Late fees, chargeback fees, returned payment fees |
| Promotional Credits | Applied discounts (shown as negative) |

---

## Autopay

- Autopay is enabled by default (78% of accounts).
- **Autopay discount:** $5/month on Premium, Unlimited, and Business plans.
- Payment methods accepted: credit card, debit card, ACH (bank account).
- Failed autopay attempts: 2 retries over 5 business days.
- After 2 failed attempts, a $5 retry fee is charged.
- Customers are notified of failed payments via SMS and email.

---

## Account Status

| Account Status | Definition |
|----------------|------------|
| Active | No balance older than 30 days |
| Past Due | Balance 15–30 days outstanding |
| Delinquent | Balance outstanding > 30 days |
| Suspended | No service; balance > 45 days |
| Prospect | No active billing account yet |
| Closed | Account terminated; final balance settled |

- Current balance carries to next invoice if unpaid.
- Service suspension at 45 days past due.
- Account closure after 90 days past due; remaining balance sent to collections.

---

## Late Fees & Penalties

| Fee Type | Amount | Trigger |
|----------|--------|---------|
| Late payment fee | $10 | Payment received after 15-day window |
| Returned payment fee | $25 | ACH or card payment returned |
| Chargeback fee | $35 | Customer-initiated chargeback |
| Paper invoice fee | $2/month | Opted into paper billing |

---

## Bill Optimization

The Aether Wireless system performs automated bill optimization reviews:

- Usage < 60% of allowance for 2 consecutive cycles → recommend downgrade.
- Multiple single lines on an account → recommend Family plan.
- Autopay not active → encourage enrollment for $5/month discount.
- Unused add-ons detected → recommend removal.

Optimization recommendations are sent via SMS and available in the app.

---

## Disputes

- Disputes must be filed within **60 days** of invoice date.
- Credit is provided for validated billing errors within 5 business days.
- Disputed amounts are held during review (no late fee accrues).
- Customers receive a case number and estimated resolution timeline.

---

## FAQs

**Q: Why is my total higher than my plan price?**
A: Total includes taxes, fees, add-ons, protection plan, and device installments.

**Q: Can I change my billing date?**
A: Billing dates are fixed by account creation; changes require manager approval and may take one cycle.

**Q: How do I get a copy of an old invoice?**
A: Available digitally for the last 24 months in the Aether Wireless app or portal.

**Q: Is there a discount for annual payment?**
A: Yes, customers who prepay 12 months receive a 10% discount on the plan charge.

---

**Contact Billing:**
- Billing Helpline: 1-833-AETHER-BILL
- Email: billing@aetherwireless.com

*Billing terms apply. Taxes vary by jurisdiction.*""",
    },

    # -------------------------------------------------------------------------
    # B.8  Payment & Eligibility Terms
    # -------------------------------------------------------------------------
    "payment_eligibility_terms.md": {
        "metadata": KnowledgeMetadata(
            title="Payment & Eligibility Terms",
            doc_id="AW-BIL-002",
            version="2.0",
            last_updated="June 2026",
            department="Finance Operations",
        ),
        "body": """## Overview

These terms define accepted payment methods, payment plan eligibility, credit requirements, and dispute resolution for billed amounts at Aether Wireless.

## Accepted Payment Methods

| Method | Availability | Notes |
|--------|-------------|-------|
| Credit card (Visa, Mastercard, Amex, Discover) | All channels | No surcharge |
| Debit card | All channels | No surcharge |
| ACH (bank account) | All channels | 3–5 business day settlement |
| In-store cash | Retail locations | Instant posting |
| In-store card | Retail locations | Instant posting |
| Digital wallet (Apple Pay, Google Pay) | App and web | Instant posting |
| Check (mailed) | Billing address only | 7–10 business day processing |

---

## Payment Method Requirements

| Method | Requirement |
|--------|-------------|
| Credit/Debit | Non-expired, valid billing address, not prepaid |
| ACH | Verified US bank account, routing + account number |
| Digital wallet | Linked funding source on file |
| Cash | Exact change not required; change given at register |

**Note:** Prepaid cards are accepted for one-time payments only, not for autopay enrollment.

---

## Payment Plans (Installments)

Eligible customers may split an outstanding balance into installments:

### Eligibility
- Account status: Active
- Tenure: 12+ months
- Minimum outstanding balance: $100
- No prior payment plan defaults in last 12 months

### Terms
- Maximum term: 3 installments (monthly payments).
- Interest: 0% for first payment plan; 5% for subsequent plans.
- Late payment fees apply per missed installment.
- Payment plan enrollment limited to once per 6 months.

### Not Eligible
- Delinquent accounts with prior defaults.
- Accounts in active fraud review.
- Accounts with balances > $500 (requires manager approval).

---

## Credit Check Requirements

| Transaction | Credit Check Required | Notes |
|-------------|----------------------|-------|
| New line (no device) | Soft pull | No impact on credit score |
| New line (with device) | Hard pull | May impact credit score |
| Device upgrade (financed) | Hard pull | For financing tier assessment |
| Plan change (no device) | No | Standard processing |

---

## Prepaid Balance / Deposits

- New customers with no credit history may be required to pay a deposit.
- Deposit range: $100–$500 based on credit assessment.
- Deposit is refundable after 12 months of on-time payments.
- Deposit is applied toward the final invoice upon account closure.

---

## Disputes

- Disputes must be filed within **60 days** of invoice date.
- Required information: invoice number, disputed amount, reason.
- Aether Wireless investigates within 5 business days.
- Credit is issued for validated errors; customer is notified of outcome.
- Disputed amounts are not subject to late fees during investigation.
- If unresolved, customers may escalate to the CFPB or state regulatory body.

---

## Auto-Pay & Reminders

- Autopay processes on the invoice date (not the due date).
- Reminder SMS sent 3 days before autopay processes.
- Reminder email sent 1 day before due date if balance is not autopay-enabled.
- Past due notices sent on days 7, 15, 30, and 45.

---

## FAQs

**Q: Can I pay from a bank account of another person?**
A: No, the funding bank account must belong to the account holder.

**Q: How quickly do payments post?**
A: Card and digital wallet payments post instantly; ACH takes 3–5 business days; checks take 7–10 business days.

**Q: Is there a fee to pay by card?**
A: No surcharge for card payment. A $25 fee applies for returned ACH payments.

**Q: Can I set up automatic partial payments?**
A: No, autopay processes the full balance. Partial payments require manual processing.

---

**Contact Billing:**
- Email: billing@aetherwireless.com
- Payment Support: 1-833-AETHER-PAY

*Payment terms apply.*""",
    },

    # -------------------------------------------------------------------------
    # B.9  Port-In Policy
    # -------------------------------------------------------------------------
    "port_in_policy.md": {
        "metadata": KnowledgeMetadata(
            title="Port-In Policy",
            doc_id="AW-SRV-001",
            version="2.5",
            last_updated="August 2026",
            department="Carrier Services",
        ),
        "body": """## Overview

Number porting brings an existing phone number from another carrier to Aether Wireless. This policy covers eligibility, timelines, required information, common failure reasons, and escalation procedures.

## Port-In Eligibility

- The number must be **active** on the losing carrier.
- Account on the losing carrier must be in good standing.
- A valid **transfer PIN (TPIN)** and account number are required.
- The number must not be mid-port from a recent move.
- The number must not be on a suspended or terminated line.
- No pending obligations (e.g., device installment balance) on losing carrier.

---

## Required Information

| Item | Description |
|------|-------------|
| Phone number | The number to port (must match losing carrier records) |
| Losing carrier account number | Found on losing carrier bill or account portal |
| Transfer PIN (TPIN) | Generated from losing carrier's app or by calling them |
| Account holder name | Must match losing carrier records exactly |
| Billing address | Must match losing carrier records exactly |
| Service address | Address where service is provided (may differ from billing) |

---

## Porting Timelines

| Scenario | Expected Timeline |
|----------|-------------------|
| Same region, all details correct | 2–4 hours |
| Cross-region / complex cases | 24–48 hours |
| Corporate / business lines | 3–5 business days |
| Prepaid to postpaid | 24–48 hours |
| International numbers | Not supported (US numbers only) |

---

## Common Failure Reasons

| Issue | Resolution |
|-------|------------|
| Incorrect TPIN | Customer requests new TPIN from losing carrier |
| Incorrect account number | Verify on losing carrier bill |
| Name/address mismatch | Customer updates records with losing carrier |
| Number on suspended line | Customer reinstates line with losing carrier |
| Pending device balance | Customer pays off balance before porting |
| Number already in port process | Wait for current port to complete |
| Losing carrier blocking port | Customer requests unblock from losing carrier |

---

## Port-In Process

1. Customer provides required information (see above).
2. Aether Wireless representative submits port request.
3. Losing carrier validates and releases the number.
4. Aether Wireless activates the number on the new SIM/eSIM.
5. Customer receives confirmation SMS when port completes.
6. Service on the losing carrier is terminated automatically.

---

## Zero-Day Trouble Resolution

For issues at activation, the **Zero-Day Experience** callback queue applies:

1. Store representative verifies port details and documents the issue.
2. Representative escalates via the internal Port Desk chat.
3. Case number is provided to the customer.
4. Port Desk investigates and resolves within 24 hours.
5. Customer is called back with status update.
6. If unresolved after 24 hours, case is escalated to carrier relations.

---

## Partial Port (Line-by-Line)

- Customers may port individual lines from a multi-line account.
- Each line is processed independently.
- Remaining lines stay with the losing carrier until ported.

---

## FAQs

**Q: Can I cancel a port before it completes?**
A: Yes, before the port completes; after activation the number is on Aether Wireless.

**Q: Can I keep both plans active during the port?**
A: No, the port transfers service; overlapping charges apply only if requested.

**Q: What if my port fails?**
A: The store resolves with the Port Desk or re-attempts with corrected details.

**Q: How long does the whole process take?**
A: Typically 2–4 hours for straightforward ports; up to 48 hours for complex cases.

**Q: Will I lose service during the port?**
A: Brief interruption (minutes) during the transfer. Keep your old SIM active until confirmation.

---

**Contact Carrier Services:**
- Port Desk: 1-833-AETHER-PORT
- Email: port@aetherwireless.com

*Ports subject to carrier schedules. US numbers only.*""",
    },

    # -------------------------------------------------------------------------
    # B.10  New Line Activation Process
    # -------------------------------------------------------------------------
    "new_line_activation_process.md": {
        "metadata": KnowledgeMetadata(
            title="New Line Activation Process",
            doc_id="AW-SRV-002",
            version="2.0",
            last_updated="July 2026",
            department="Retail Operations",
        ),
        "body": """## Overview

This document covers the end-to-end process for activating a new line at Aether Wireless, including identity verification, credit checks, SIM/eSIM provisioning, and first-bill expectations.

## Pre-Approval Steps

1. Verify identity with two valid documents (ID + address proof).
2. Run credit check if financing a device.
3. Confirm customer consent for KYC data storage.
4. Select plan and device (or bring-your-own-device).
5. Review and accept Aether Wireless Terms of Service.
6. Collect activation fee (if applicable).

---

## Identity Verification

| Requirement | Accepted Documents | Validity |
|-------------|-------------------|----------|
| Identity | Passport, driver license, national ID, military ID | Must be current/valid |
| Address | Utility bill, bank statement, lease agreement | Within 90 days |
| In-store biometric | Fingerprint or facial scan (optional) | Immediate |
| Online activation | Video verification or uploaded ID scan | Processed within 1 hour |

---

## Credit Check

| Transaction | Credit Check Type | Impact |
|-------------|-------------------|--------|
| New line (BYOD) | Soft pull | No score impact |
| New line (with device) | Hard pull | Temporary score impact |
| New line (prepaid) | None | N/A |

- Credit results are valid for 30 days.
- Customers with limited credit may be required to pay a deposit ($100–$500).
- Credit tier determines device financing limits (see Device Upgrade Guidelines).

---

## SIM / eSIM Provisioning

### Physical SIM
- In-store: Instant provisioning from Aether Wireless SIM inventory.
- Online: SIM shipped within 2 business days (free shipping).
- SIM types: Nano, Micro, Standard (adapter included).

### eSIM
- QR code issued in-store or via email.
- Activation within minutes.
- Compatible devices: iPhone XS+, Samsung Galaxy S20+, Google Pixel 3+.
- Dual SIM supported on compatible devices.

### Remote Provisioning (Aether Wireless Phase 4+)
- Service callbacks activate eSIM without store visit.
- Customer receives QR code via email or app.
- Self-service activation through the Aether Wireless app.

---

## Activation Flow

1. System creates the account and assigns billing cycle date.
2. SIM/eSIM is provisioned and activated.
3. Customer receives welcome SMS within 2 minutes.
4. Welcome email with account details, app download link, and support contacts.
5. First bill includes prorated charges from activation date to end of billing cycle.
6. 14-day return window starts at activation date.

---

## Activation Fees

| Plan | Activation Fee | Waiver Conditions |
|------|---------------|-------------------|
| Essential | $35 | Waived with 2-year commitment |
| Standard | $35 | Waived with Premium+ plan or autopay |
| Premium | $0 | Waived |
| Family | $0 | Waived |
| Unlimited | $0 | Waived |
| Business | $0 | Waived |
| Senior | $0 | Waived |

---

## First Bill Expectations

- Prorated plan charge for days remaining in billing cycle.
- Full month of plan charge for the new cycle.
- Taxes and regulatory fees.
- Activation fee (if applicable).
- Device installment (if applicable, first payment).
- Protection plan (if enrolled, first payment).
- Promotional credits (if applicable, shown as negative line item).

---

## BYOD (Bring Your Own Device) Activation

- Device must be unlocked from previous carrier.
- Device must be compatible with Aether Wireless network bands.
- IMEI check available at aetherwireless.com/byod.
- BYOD customers receive a $50 account credit.

---

## FAQs

**Q: How long does activation take?**
A: 5–10 minutes in-store with correct documentation; up to 1 hour online.

**Q: Can I activate my own device?**
A: Yes (BYOD); only plan and SIM/eSIM required.

**Q: What if I lose my SIM?**
A: Replacement SIM issued in 10 minutes in-store; eSIM re-issued via app or email.

**Q: Can I activate multiple lines at once?**
A: Yes, each line is processed independently. Family plan lines are activated together.

**Q: Do I need to be at a store?**
A: No, online and phone activation are available for most scenarios.

---

**Contact Retail Operations:**
- Retail Helpline: 1-833-AETHER-RTL
- Email: activations@aetherwireless.com

*Activation terms apply. Subject to credit approval.*""",
    },

    # -------------------------------------------------------------------------
    # B.11  Returns & Refunds Policy
    # -------------------------------------------------------------------------
    "returns_refunds_policy.md": {
        "metadata": KnowledgeMetadata(
            title="Returns & Refunds Policy",
            doc_id="AW-SRV-003",
            version="3.2",
            last_updated="August 2026",
            department="Retail Operations",
        ),
        "body": """## Overview

Customers may return devices and cancel lines within a cooling-off period. This policy defines return windows, restocking fees, refund mechanics, and device condition requirements.

## Return Windows

| Scenario | Window | Restocking Fee |
|----------|--------|----------------|
| New device (in-store or online) | 14 days | $35 (waived for DOA) |
| eSIM / activation only (no device) | 14 days | None |
| Open-box / refurbished device | 7 days | $35 |
| Accessory return (unopened) | 30 days | None |
| Accessory return (opened) | 14 days | None |

---

## Refund Mechanics

- Full refund to original payment method within **7–10 business days**.
- Activation fee is refunded when the full line is canceled within the return window.
- Plan charges for days used are deducted from the refund.
- Device installment payments made are refunded.
- Promotional credits applied at purchase are deducted from the refund.

---

## Device Return Conditions

### Acceptable Condition
- Device must be returned with original packaging and accessories.
- No cracks on screen or body.
- No liquid damage indicators triggered.
- Activation lock must be removed (iCloud, Google account, etc.).
- Factory reset completed before return.

### Condition Assessment

| Condition | Action |
|-----------|--------|
| Like new | Full refund, no restocking fee |
| Minor cosmetic wear | Full refund, $35 restocking fee |
| Screen crack | 50% refund, $35 restocking fee |
| Liquid damage | No refund, device returned to customer |
| Missing accessories | Deduction of accessory value from refund |

---

## DoA (Dead on Arrival)

- Reported within 14 days of activation.
- Device must power on but fail to function as intended.
- Replacement shipped next business day (or available in-store).
- No restocking fee.
- Return shipping paid by Aether Wireless.
- Customer may request a refund instead of replacement.

---

## Return Process

1. Customer initiates return via app, website, or in-store.
2. Representative verifies purchase date and return window.
3. Device diagnostics run in-store (or return label issued for online purchases).
4. Return is processed per policy above.
5. Refund issued within 7–10 business days of device receipt.
6. Line is canceled or replaced; plan charges adjusted.
7. Customer receives refund confirmation via email.

---

## Online / Phone Returns

- Online purchases can be returned in-store or by mail.
- Prepaid return label provided for mail returns.
- Return shipping is free for defective/DOA items.
- Customer pays return shipping for change-of-mind returns ($10 deducted from refund).
- Mail returns must be postmarked within the return window.

---

## Non-Returnable Items

- Gift cards and prepaid airtime.
- Activated software or digital content.
- Devices reported lost or stolen.
- Devices with third-party repairs.
- Accessories that have been personalized.

---

## FAQs

**Q: Can I return an activated device?**
A: Yes, within the 14-day window, subject to conditions above.

**Q: Who pays return shipping?**
A: Aether Wireless pays for factory defects and DOA; customer pays for change-of-mind returns.

**Q: When will I see my refund?**
A: Within 7–10 business days of device receipt at our facility.

**Q: Can I exchange instead of return?**
A: Yes, exchanges are processed as a return + new purchase. Price differences are refunded or charged.

**Q: What if I return after 14 days?**
A: Returns after 14 days are not accepted. Consider filing a protection claim if the device is defective.

---

**Contact Retail Operations:**
- Email: returns@aetherwireless.com
- Return Support: 1-833-AETHER-RTL

*Returns policy applies. See full Terms of Service for details.*""",
    },

    # -------------------------------------------------------------------------
    # B.12  Promotions & Offer Eligibility Terms
    # -------------------------------------------------------------------------
    "promotions_eligibility_terms.md": {
        "metadata": KnowledgeMetadata(
            title="Promotions & Offer Eligibility Terms",
            doc_id="AW-PRO-001",
            version="2.0",
            last_updated="August 2026",
            department="Marketing Operations",
        ),
        "body": """## Overview

Promotions and offers provide discounts on plans, devices, and bundles. This document defines the offer catalog, eligibility rules, stacking policies, and terms for each promotion.

## Offer Catalog

| Offer ID | Name | Type | Benefit | Valid Until |
|----------|------|------|---------|-------------|
| PROMO-0001 | Premium Upgrade Discount | Plan offer | $10/mo off Premium for 12 months | Dec 2026 |
| PROMO-0002 | Family Bundle Deal | Plan offer | $15/mo off Family with 2+ lines | Dec 2026 |
| PROMO-0003 | New Device Trade-In Bonus | Device promo | $200 off flagship with trade-in | Dec 2026 |
| PROMO-0004 | Premium + Pixel Bundle | Bundle | Premium + Pixel 9, $150 off | Nov 2026 |
| PROMO-0005 | Win-Back Unlimited Offer | Plan offer | Unlimited at $75/mo for 6 months | Dec 2026 |
| PROMO-0006 | Referral Bonus | Account credit | $50 credit for referrer + referee | Dec 2026 |
| PROMO-0007 | Senior Plan Promo | Plan offer | Senior plan at $25/mo for 12 months | Dec 2026 |
| PROMO-0008 | Holiday Bundle Special | Bundle | Family plan + 2 devices, $300 off | Jan 2027 |

---

## Eligibility by Account Status

| Account Status | Eligible Offers |
|----------------|-----------------|
| Active | PROMO-0001, PROMO-0002, PROMO-0003, PROMO-0004, PROMO-0006 |
| Prospect | PROMO-0001, PROMO-0003, PROMO-0007 |
| Delinquent | PROMO-0005 (win-back only) |
| Senior (65+) | PROMO-0007 |

---

## Offer Matching Rules

- Representative matches offers based on account status, plan, and customer intent.
- A maximum of **2 offers** may be presented per customer interaction.
- Bundles (PROMO-0004, PROMO-0008) cannot stack with individual plan or device offers.
- Win-back offers (PROMO-0005) are exclusive to delinquent accounts.
- Referral bonus (PROMO-0006) requires a valid referral code from an existing customer.

---

## Stacking Rules

| Combination | Allowed |
|-------------|---------|
| Plan discount + device trade-in | Yes |
| Plan discount + bundle | No |
| Two plan discounts | No |
| Win-back + any other offer | No |
| Referral credit + plan discount | Yes |
| Referral credit + device promo | Yes |
| Two device promos | No |
| Bundle + referral credit | No |

---

## Offer Duration & Expiry

| Offer Type | Duration | Notes |
|------------|----------|-------|
| Plan discounts | 12 months (or stated) | Returns to standard price after |
| Device credits | Instant at purchase | One-time credit |
| Bundle offers | Duration of bundle commitment | Early cancellation forfeits discount |
| Referral credits | One-time | Credited within 30 days |
| Win-back offers | 6 months | Extended if customer remains active |

- Promotions expire at the `valid_until` date of the offer.
- Customers are notified 30 days before promotional pricing expires.
- Expired promotions cannot be reactivated.

---

## Promotional Terms

- All promotions are subject to availability.
- Aether Wireless reserves the right to modify or withdraw promotions at any time.
- Promotions are non-transferable and have no cash value.
- Fraudulent use of promotions results in account review and potential termination.
- Promotional pricing does not apply to taxes and regulatory fees.

---

## Customer Communication

- Promotional offers are communicated via: SMS, email, app notifications, and in-store signage.
- Customers may opt out of promotional communications at any time.
- Opt-out does not affect active promotional pricing.

---

## FAQs

**Q: Can I get two promotions on one order?**
A: Yes, a plan offer plus a device promo (subject to stacking rules).

**Q: What happens after a discount expires?**
A: The plan returns to its standard price; you are notified 30 days in advance.

**Q: Why was I not offered a promotion?**
A: Eligibility is based on account status, plan type, and current promotions.

**Q: Can I combine my referral credit with a trade-in?**
A: Yes, referral credits and device trade-in bonuses can be combined.

**Q: What if I cancel my line during a promotion?**
A: The promotional discount is forfeited; standard early termination fees may apply.

---

**Contact Marketing:**
- Email: offers@aetherwireless.com
- Promotions Support: 1-833-AETHER-PROMO

*Offers subject to availability. Terms and conditions apply.*""",
    },

    # -------------------------------------------------------------------------
    # B.13  International Roaming Policy  (NEW)
    # -------------------------------------------------------------------------
    "international_roaming_policy.md": {
        "metadata": KnowledgeMetadata(
            title="International Roaming Policy",
            doc_id="AW-SRV-004",
            version="1.2",
            last_updated="August 2026",
            department="Carrier Services",
        ),
        "body": """## Overview

Aether Wireless provides international roaming services in 180+ countries. This policy covers roaming passes, rates, data management, and troubleshooting.

## Roaming Passes

| Pass | Price | Data | Calls | SMS | Validity |
|------|-------|------|-------|-----|----------|
| Day Pass | $15/day | 500 MB high-speed | Unlimited in-country | Unlimited in-country | 24 hours |
| Weekly Pass | $50/week | 3 GB high-speed | Unlimited in-country | Unlimited in-country | 7 days |
| Monthly Pass | $120/month | 10 GB high-speed | Unlimited in-country + US | Unlimited | 30 days |
| Cruise Pass | $10/day | 200 MB | $1.50/min | $0.50/day | 24 hours |

---

## Pay-Per-Use Rates (Without Pass)

| Service | Rate |
|---------|------|
| Data | $2/MB |
| Calls received | $1.50/minute |
| Calls made | $2.00/minute |
| SMS sent | $0.50/message |
| SMS received | Free |
| MMS | $1.00/message |

---

## Coverage Regions

| Region | Countries | Network Partners |
|--------|-----------|-----------------|
| North America | US, Canada, Mexico | Rogers, Telcel, Bell |
| Europe | 35+ countries | Vodafone, Orange, Deutsche Telekom |
| Asia-Pacific | 25+ countries | SoftBank, Singtel, Optus |
| Latin America | 20+ countries | Claro, Entel, Movistar |
| Africa | 15+ countries | MTN, Vodacom, Safaricom |
| Middle East | 10+ countries | Etisalat, STC, Zain |

---

## Roaming Activation

- Roaming is disabled by default for security.
- Enable via: Aether Wireless app → Settings → International Roaming.
- Enable via: aetherwireless.com → Account → Roaming Settings.
- Enable via: Call 1-833-AETHER-INTL.
- Activation is instant; no reboot required.

---

## Data Management While Roaming

- Real-time data usage notifications at 50%, 80%, and 100% of pass allowance.
- Auto-purchase of additional day pass if data is exhausted.
- Customers can set data roaming limits in the app.
- Data saver mode recommended: disables background app refresh.

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| No service abroad | Toggle airplane mode; wait 5 minutes |
| Can't make calls | Check roaming is enabled; verify pass is active |
| Slow data | Network congestion; try switching to 3G/4G |
| Unexpected charges | Review pass activation date; contact support |

---

## FAQs

**Q: Do I need to activate roaming before travel?**
A: Yes, enable roaming in the app at least 24 hours before departure.

**Q: Will I be charged if I don't use my phone abroad?**
A: No charges unless you make/receive calls, send SMS, or use data.

**Q: Can I use my domestic data allowance abroad?**
A: Only with the Monthly Pass. Day and Weekly passes have separate allowances.

---

**Contact Carrier Services:**
- International Support: 1-833-AETHER-INTL
- Email: roaming@aetherwireless.com

*Rates subject to change. See partner network terms for details.*""",
    },

    # -------------------------------------------------------------------------
    # B.14  Loyalty & Rewards Program  (NEW)
    # -------------------------------------------------------------------------
    "loyalty_rewards_program.md": {
        "metadata": KnowledgeMetadata(
            title="Loyalty & Rewards Program",
            doc_id="AW-PRO-002",
            version="1.0",
            last_updated="August 2026",
            department="Marketing Operations",
        ),
        "body": """## Overview

Aether Rewards is the loyalty program for Aether Wireless customers. Members earn points on eligible purchases and monthly service charges, redeemable for discounts, devices, and experiences.

## Membership Tiers

| Tier | Points Required | Benefits |
|------|-----------------|----------|
| Silver | 0 (auto-enrolled) | 1 point per $1 spent, basic rewards |
| Gold | 5,000 points | 1.5 points per $1, priority support, early access to deals |
| Platinum | 15,000 points | 2 points per $1, free device upgrade once/year, concierge support |
| Diamond | 30,000 points | 2.5 points per $1, exclusive events, annual gift |

---

## Earning Points

| Activity | Points Earned |
|----------|---------------|
| Monthly service charge | 1 point per $1 |
| Device purchase | 2 points per $1 |
| Accessory purchase | 1 point per $1 |
| Referring a new customer | 500 bonus points |
| On-time payment (12 months) | 200 bonus points |
| Enrolling in autopay | 100 bonus points |
| Completing a survey | 50 points |
| Birthday bonus | 200 points |

---

## Redemption

| Reward | Points Required |
|--------|-----------------|
| $5 account credit | 500 points |
| $10 account credit | 1,000 points |
| Free accessory (up to $50 value) | 2,500 points |
| $100 device credit | 5,000 points |
| Free month of service | 7,500 points |
| Device upgrade discount (up to $500) | 15,000 points |
| Exclusive event access | 10,000 points |

---

## Point Expiration

- Points expire after **24 months** of account inactivity.
- Account inactivity = no earning or redemption activity.
- Expiration reminders sent 60 and 30 days before expiry.
- Tier status resets annually based on 12-month rolling point total.

---

## Terms & Conditions

- Points have no cash value and cannot be transferred.
- Aether Wireless reserves the right to modify the rewards program.
- Fraudulent point accumulation results in account suspension.
- Points earned during promotional periods are subject to promotional terms.
- Rewards are subject to availability.

---

## FAQs

**Q: How do I check my points balance?**
A: Via the Aether Wireless app → Rewards tab, or call 1-833-AETHER-REW.

**Q: Can I use points to pay my bill?**
A: Yes, redeem for account credits applied to your next invoice.

**Q: Do points transfer if I change my number?**
A: Yes, points are tied to your account, not your number.

---

**Contact Rewards:**
- Email: rewards@aetherwireless.com

*Aether Rewards program terms apply.*""",
    },

    # -------------------------------------------------------------------------
    # B.15  Network Service Level Agreement  (NEW)
    # -------------------------------------------------------------------------
    "network_service_level_agreement.md": {
        "metadata": KnowledgeMetadata(
            title="Network Service Level Agreement",
            doc_id="AW-NET-001",
            version="1.1",
            last_updated="July 2026",
            department="Network Operations",
        ),
        "body": """## Overview

This document defines Aether Wireless's network performance commitments, service level targets, and remedies for customers affected by outages or degradation.

## Network Uptime Commitment

| Metric | Target | Measurement |
|--------|--------|-------------|
| Network availability | 99.9% monthly | Excluding scheduled maintenance |
| Voice call completion rate | 99.5% | Per 1,000 call attempts |
| SMS delivery rate | 99.9% | Per 1,000 messages |
| Data session success rate | 99.5% | Per 1,000 data session attempts |
| 4G/5G coverage | 98% of service area | Population-weighted |

---

## Scheduled Maintenance

- Maintenance windows: 2:00 AM – 6:00 AM local time.
- Customers notified 72 hours in advance via SMS and email.
- No more than 4 maintenance windows per month.
- Emergency maintenance exempt from notification requirement.

---

## Outage Response

| Severity | Definition | Response Time | Resolution Target |
|----------|-----------|---------------|-------------------|
| Critical | Complete service loss in major metro area | 15 minutes | 4 hours |
| Major | Service degradation in metro area | 30 minutes | 8 hours |
| Moderate | Localized outage (< 10,000 users) | 1 hour | 12 hours |
| Minor | Single-site or edge issue | 4 hours | 24 hours |

---

## Service Credits

Customers may be eligible for service credits when network SLA targets are not met:

| Outage Duration | Credit Amount |
|-----------------|---------------|
| 2–4 hours | $5 account credit |
| 4–8 hours | $10 account credit |
| 8–24 hours | $20 account credit |
| 24+ hours | $50 account credit + prorated daily plan charge |

- Credits are applied automatically for outages > 4 hours.
- Customers may request credit for shorter outages via Customer Care.
- Credits are limited to one per event per line.

---

## Coverage & Speed Guarantees

| Metric | Target |
|--------|--------|
| Average download speed | 25 Mbps (4G), 100 Mbps (5G) |
| Average upload speed | 10 Mbps (4G), 20 Mbps (5G) |
| Latency | < 50ms (4G), < 20ms (5G) |
| Coverage map accuracy | 95% of marked areas |

---

## Performance Reporting

- Monthly network performance reports available at aetherwireless.com/network.
- Real-time outage map at aetherwireless.com/status.
- Network quality data shared quarterly with regulatory bodies.

---

## FAQs

**Q: How do I report a network issue?**
A: Via the app (Settings → Report Issue), online, or by calling 1-833-AETHER-NET.

**Q: Will I be credited for every outage?**
A: Credits apply for outages > 4 hours. Shorter outages may qualify upon request.

**Q: How accurate is the coverage map?**
A: Coverage maps are updated quarterly and reflect 95% of actual coverage areas.

---

**Contact Network Operations:**
- Network Support: 1-833-AETHER-NET
- Email: network@aetherwireless.com

*Service level commitments subject to force majeure events.*""",
    },

    # -------------------------------------------------------------------------
    # B.16  Privacy & Data Protection Policy  (NEW)
    # -------------------------------------------------------------------------
    "privacy_data_protection_policy.md": {
        "metadata": KnowledgeMetadata(
            title="Privacy & Data Protection Policy",
            doc_id="AW-LEG-001",
            version="1.0",
            last_updated="August 2026",
            department="Legal & Compliance",
        ),
        "body": """## Overview

Aether Wireless is committed to protecting customer privacy and personal data. This policy describes what data is collected, how it is used, and customer rights under applicable privacy laws.

## Data Collected

| Category | Examples | Purpose |
|----------|----------|---------|
| Account information | Name, address, email, phone | Service provisioning, billing |
| Payment information | Card numbers, bank accounts | Payment processing |
| Device information | IMEI, device model, OS version | Device management, support |
| Usage data | Call logs, data usage, SMS metadata | Service optimization, billing |
| Location data | Cell tower connections, GPS (with consent) | Network optimization, emergency services |
| App usage | Aether Wireless app interactions | Service improvement |
| Support interactions | Call recordings, chat transcripts | Quality assurance, dispute resolution |

---

## Data Usage Principles

- Data is collected only for stated purposes.
- Data is not sold to third parties.
- Data is shared only with service providers under contract.
- Data is retained only as long as necessary.
- Customers can request data deletion (subject to legal retention requirements).

---

## Customer Rights

| Right | Description | How to Exercise |
|-------|-------------|-----------------|
| Access | Request a copy of your personal data | App → Privacy → Data Request |
| Correction | Request correction of inaccurate data | App → Privacy → Update Info |
| Deletion | Request deletion of your data | App → Privacy → Delete Request |
| Portability | Request data in machine-readable format | App → Privacy → Export Data |
| Opt-out | Opt out of marketing data use | App → Privacy → Marketing Opt-Out |
| Restrict processing | Limit how your data is used | App → Privacy → Processing Settings |

---

## Third-Party Sharing

| Recipient | Purpose | Safeguards |
|-----------|---------|------------|
| Payment processors | Payment handling | PCI-DSS compliant |
| Network equipment vendors | Network optimization | Data anonymized |
| Customer support platforms | Service delivery | Encrypted, access-controlled |
| Regulatory bodies | Legal compliance | Per applicable law |

---

## Data Security

- All data encrypted at rest (AES-256) and in transit (TLS 1.3).
- Multi-factor authentication for customer accounts.
- Regular security audits and penetration testing.
- Employee access to customer data is logged and monitored.
- Incident response plan in place with 72-hour breach notification.

---

## Data Retention

| Data Type | Retention Period |
|-----------|-----------------|
| Account information | Duration of account + 7 years |
| Payment records | 7 years (regulatory requirement) |
| Call/SMS metadata | 18 months |
| Location data | 12 months |
| Support interactions | 3 years |
| App usage data | 24 months |

---

## Children's Privacy

- Aether Wireless does not knowingly collect data from children under 13.
- Parental consent required for minors (under 18) on family accounts.

---

## Policy Updates

- Material changes communicated 30 days in advance.
- Non-material updates posted on the Aether Wireless website.
- Continued use of services constitutes acceptance of updated policy.

---

## FAQs

**Q: Does Aether Wireless sell my data?**
A: No. We do not sell personal data to third parties.

**Q: How do I request my data?**
A: Via the Aether Wireless app under Privacy Settings, or by emailing privacy@aetherwireless.com.

**Q: How long is my data kept?**
A: See the retention table above. Most data is retained for the duration of your account plus a legal holding period.

---

**Contact Privacy:**
- Email: privacy@aetherwireless.com
- Data Protection Officer: dpo@aetherwireless.com

*Privacy policy compliant with CCPA, GDPR, and applicable state privacy laws.*""",
    },
}


# ==============================================================================
# 3. EXECUTION & OUTPUT TO data/policies
# ==============================================================================

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Successfully generated knowledge base under '{OUTPUT_DIR.resolve()}':")
    count = 0
    for filename, spec in KB.items():
        path = OUTPUT_DIR / filename
        rendered = KnowledgeDocument(metadata=spec["metadata"], body=spec["body"]).rendered
        path.write_text(rendered, encoding="utf-8")
        print(f" - {path}")
        count += 1
    print(f"\nTotal: {count} documents generated.")


if __name__ == "__main__":
    main()
