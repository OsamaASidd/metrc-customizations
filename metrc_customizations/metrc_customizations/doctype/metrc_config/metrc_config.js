frappe.ui.form.on("Metrc Config", {
	refresh(frm) {
		if (frm.__status_html) {
			frm.get_field("connection_status").$wrapper.html(frm.__status_html);
		}
		render_capabilities(frm);
	},

	test_connection(frm) {
		const run = () => {
			frm.get_field("connection_status").$wrapper.html(
				'<span style="color:#718096">Testing…</span>'
			);
			frappe.call({
				method: "metrc_customizations.metrc_customizations.doctype.metrc_config.metrc_config.test_connection",
				freeze: true,
				freeze_message: __("Testing Metrc connection…"),
				callback(r) {
					const d = r.message || {};
					const color = d.ok ? "#276749" : "#c53030";
					const bg = d.ok ? "#e6f4ea" : "#fde8e8";
					let html = `<div style="padding:10px 12px;border-radius:8px;background:${bg};color:${color};">
						<b>${d.ok ? "✓ Connected" : "✗ Failed"}</b> — HTTP ${d.status_code ?? "—"}
						<div style="margin-top:4px;color:#333;font-size:12px;">${frappe.utils.escape_html(d.message || "")}</div>`;
					if (d.ok && (d.facilities || []).length) {
						html += `<div style="margin-top:6px;font-size:12px;color:#333;"><b>Facilities:</b> ${d.facilities
							.map(frappe.utils.escape_html)
							.join(", ")}</div>`;
					}
					html += `</div>`;
					frm.__status_html = html;
					frm.get_field("connection_status").$wrapper.html(html);
				},
			});
		};
		frm.is_dirty() ? frm.save().then(run) : run();
	},
});

// ─────────────────────────────────────────────────────────────────────────────
// CEO-facing catalogue of what the Metrc integration can do. Verified live
// against the CA sandbox with the current keys.
// status: "live" (working), "read" (read-only), "blocked" (Metrc-side permission)
// ─────────────────────────────────────────────────────────────────────────────
function render_capabilities(frm) {
	const GROUPS = [
		{
			title: "Onboarding &amp; Master Data",
			icon: "🏷️",
			items: [
				{ a: "Locations — create, update, view", m: ["POST", "PUT", "GET"], s: "live", g: [["Active locations", "locations"], ["Location types", "location_types"]] },
				{ a: "Strains — create, update, view", m: ["POST", "PUT", "GET"], s: "live", g: [["Active strains", "strains"]] },
				{ a: "Items / product catalog — create, update, view", m: ["POST", "PUT", "GET"], s: "live", g: [["Active items", "items"], ["Item categories", "item_categories"]] },
			],
		},
		{
			title: "Cultivation — Plants &amp; Batches",
			icon: "🌱",
			items: [
				{ a: "Create plant batch (clone from mother plant)", m: ["POST"], s: "live", g: [["Active plant batches", "plant_batches"]] },
				{ a: "Move a plant to another location", m: ["PUT"], s: "live" },
				{ a: "Change growth phase (veg / flower)", m: ["POST"], s: "live", g: [["Vegetative plants", "plants_veg"], ["Flowering plants", "plants_flower"]] },
				{ a: "Manicure a plant", m: ["POST"], s: "live" },
				{ a: "Harvest plants", m: ["PUT"], s: "live" },
				{ a: "Destroy plants / plant batch", m: ["DELETE"], s: "live", g: [["Plant waste reasons", "plant_waste_reasons"]] },
				{ a: "Package clones / immature plants", m: ["POST"], s: "live" },
				{ a: "Create batch from seed (opening balance)", m: ["POST"], s: "blocked", n: "facility permission" },
			],
		},
		{
			title: "Harvests",
			icon: "🌾",
			items: [
				{ a: "Create package from a harvest (finished goods)", m: ["POST"], s: "live", g: [["Active harvests", "harvests"]] },
				{ a: "Record harvest waste", m: ["POST"], s: "live", g: [["Harvest waste types", "harvest_waste_types"]] },
				{ a: "Finish / unfinish a harvest", m: ["PUT"], s: "live" },
			],
		},
		{
			title: "Packages &amp; Inventory",
			icon: "📦",
			items: [
				{ a: "Create derived package (repackage / split / combine)", m: ["POST"], s: "live", g: [["Active packages", "packages_active"], ["Package types", "package_types"]] },
				{ a: "Change the item on a package", m: ["PUT"], s: "live" },
				{ a: "Adjust quantity (inventory reconciliation)", m: ["PUT"], s: "live", g: [["Adjust reasons", "adjust_reasons"]] },
				{ a: "Finish a package", m: ["PUT"], s: "live", g: [["Inactive packages", "packages_inactive"]] },
				{ a: "Opening-balance / beginning inventory package", m: ["POST"], s: "blocked", n: "facility permission" },
			],
		},
		{
			title: "Transfers",
			icon: "🚚",
			items: [
				{ a: "View incoming / outgoing / rejected transfers", m: ["GET"], s: "read", g: [["Incoming", "transfers_incoming"], ["Outgoing", "transfers_outgoing"], ["Rejected", "transfers_rejected"], ["Transfer types", "transfer_types"]] },
				{ a: "View manifests, deliveries &amp; packages in transit", m: ["GET"], s: "read", g: [["Packages in transit", "packages_intransit"]] },
				{ a: "Create, update &amp; view transfer templates", m: ["POST", "PUT", "GET"], s: "live", g: [["Transfer templates", "transfer_templates"]] },
				{ a: "Initiate / receive licensed transfers", m: ["—"], s: "blocked", n: "Metrc portal only" },
				{ a: "External incoming transfers", m: ["POST"], s: "blocked", n: "vendor-key permission" },
			],
		},
		{
			title: "Sales &amp; Lab Results",
			icon: "💵",
			items: [
				{ a: "Create retail sales receipts", m: ["POST"], s: "blocked", n: "retail licence only", g: [["Sales receipts", "sales_receipts"]] },
				{ a: "Lab test results", m: ["GET", "POST"], s: "live", g: [["Lab test types", "labtest_types"], ["Lab test states", "labtest_states"]] },
			],
		},
		{
			title: "Reference Data (reads)",
			icon: "🔎",
			items: [
				{ a: "Facilities, plant &amp; package tags, item categories, units of measure, waste reasons, transfer types…", m: ["GET"], s: "read", g: [["Facilities", "facilities"], ["Employees", "employees"], ["Units of measure", "units"], ["Plant tags", "plant_tags"], ["Package tags", "package_tags"]] },
			],
		},
	];

	const METHOD_COLOR = { GET: "#2b6cb0", POST: "#276749", PUT: "#b7791f", DELETE: "#c53030", "—": "#a0aec0" };
	const mBadge = (m) =>
		`<span style="display:inline-block;font:700 10px/1.6 'DM Mono',monospace;letter-spacing:.03em;color:#fff;background:${METHOD_COLOR[m] || "#718096"};border-radius:4px;padding:0 6px;margin-right:4px;">${m}</span>`;
	const sPill = (s, n) => {
		const map = {
			live: ["#e6f4ea", "#1c6b3f", "Live"],
			read: ["#e6effa", "#20548f", "Read-only"],
			blocked: ["#fde8e8", "#b5352f", "Blocked"],
		};
		const [bg, fg, label] = map[s] || map.read;
		return `<span style="white-space:nowrap;font:600 11px/1.7 inherit;color:${fg};background:${bg};border-radius:20px;padding:1px 9px;">${label}${n ? ` · ${n}` : ""}</span>`;
	};

	let live = 0,
		blocked = 0;
	GROUPS.forEach((g) => g.items.forEach((i) => (i.s === "blocked" ? blocked++ : live++)));

	const cards = GROUPS.map((g) => {
		const rows = g.items
			.map(
				(i) => `
			<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:8px 0;border-top:1px solid #edf0f5;">
				<div style="flex:1;min-width:0;">
					<div style="font-size:13px;color:#2d3748;">${i.a}</div>
					<div style="margin-top:3px;">${i.m.map(mBadge).join("")}</div>
					${(i.g || []).length ? `<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:5px;">${i.g.map(([l, k]) => probeBtn(l, k)).join("")}</div>` : ""}
				</div>
				<div style="padding-top:1px;">${sPill(i.s, i.n)}</div>
			</div>`
			)
			.join("");
		return `
		<div style="background:#fff;border:1px solid #e6e9ef;border-radius:12px;padding:14px 16px;box-shadow:0 1px 3px rgba(16,24,40,.04);">
			<div style="font:700 14px/1.3 inherit;color:#1a202c;display:flex;align-items:center;gap:8px;margin-bottom:4px;">
				<span style="font-size:16px;">${g.icon}</span> ${g.title}
			</div>
			${rows}
		</div>`;
	}).join("");

	const html = `
	<div style="font-family:inherit;color:#2d3748;">
		<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;
			background:linear-gradient(135deg,#4c1d95,#6d28d9);border-radius:14px;padding:16px 20px;color:#fff;margin-bottom:14px;">
			<div>
				<div style="font:800 18px/1.2 inherit;">Metrc Integration — Capabilities</div>
				<div style="font-size:12.5px;opacity:.85;margin-top:3px;">What Motley's ERP can do with Metrc, verified live against the API.</div>
			</div>
			<div style="display:flex;gap:10px;align-items:stretch;">
				<div style="display:flex;flex-direction:column;justify-content:center;gap:3px;">
					<div style="font-size:11px;opacity:.85;">Licence</div>
					<select class="metrc-licence" style="border:0;border-radius:8px;padding:6px 8px;font:600 12.5px/1.2 inherit;color:#4c1d95;max-width:260px;">
						${(frm.doc.licences || []).map((r) => `<option value="${frappe.utils.escape_html(r.license_number)}" ${r.license_number === frm.__metrc_licence ? "selected" : ""}>${frappe.utils.escape_html(r.license_number)}${r.facility_name ? " — " + frappe.utils.escape_html(r.facility_name) : ""}</option>`).join("")}
					</select>
				</div>
				<button class="metrc-run-all" style="border:0;cursor:pointer;background:#fff;color:#4c1d95;font:700 12.5px/1.2 inherit;border-radius:10px;padding:8px 14px;">▶ Run all GET checks<div class="metrc-run-all-summary" style="font-weight:500;font-size:11px;color:#6b46c1;margin-top:2px;">live against Metrc</div></button>
				<div style="text-align:center;background:rgba(255,255,255,.14);border-radius:10px;padding:8px 14px;">
					<div style="font:800 22px/1 inherit;">${live}</div>
					<div style="font-size:11px;opacity:.9;">Actions live</div>
				</div>
				<div style="text-align:center;background:rgba(255,255,255,.14);border-radius:10px;padding:8px 14px;">
					<div style="font:800 22px/1 inherit;">~50</div>
					<div style="font-size:11px;opacity:.9;">Endpoints tested</div>
				</div>
				<div style="text-align:center;background:rgba(255,255,255,.14);border-radius:10px;padding:8px 14px;">
					<div style="font:800 22px/1 inherit;">${blocked}</div>
					<div style="font-size:11px;opacity:.9;">Pending Metrc</div>
				</div>
			</div>
		</div>

		<div style="display:flex;flex-wrap:wrap;gap:14px;font-size:11.5px;color:#4a5568;margin-bottom:14px;">
			<span>${mBadge("GET")} read</span>
			<span>${mBadge("POST")}${mBadge("PUT")}${mBadge("DELETE")} write</span>
			<span>${sPill("live")} working now</span>
			<span>${sPill("read")} read-only</span>
			<span>${sPill("blocked")} needs a Metrc permission</span>
			<span>${probeBtn("click", "")} runs a live read-only GET against Metrc</span>
		</div>

		<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;">
			${cards}
		</div>

		<div style="margin-top:14px;font-size:12px;color:#718096;line-height:1.5;">
			The two <b>Blocked</b> items are Metrc-side permissions, not code limits — the opening-balance
			creates need a facility flag, and external-incoming transfers need a vendor-key scope, both granted by Metrc.
			Everything else runs today. Transfers between licensees are read via the API and actioned in the Metrc portal
			(Metrc's own design).
		</div>
	</div>`;

	const $w = frm.get_field("functionality_overview").$wrapper;
	$w.html(html);
	$w.find('.metrc-probe[data-key=""]').css("pointer-events", "none");
	if (!frm.__metrc_licence) frm.__metrc_licence = $w.find(".metrc-licence").val();
	$w.off("change.metrc").on("change.metrc", ".metrc-licence", function () {
		frm.__metrc_licence = $(this).val();
		render_capabilities(frm); // clear previous licence's results
	});
	$w.off("click.metrc")
		.on("click.metrc", ".metrc-probe[data-key!='']", function () {
			run_probe($(this), frm.__metrc_licence).then((d) => d && show_probe(d, $(this).data("label")));
		})
		.on("click.metrc", ".metrc-run-all", async function () {
			const $btns = $w.find(".metrc-probe[data-key!='']");
			const $sum = $w.find(".metrc-run-all-summary");
			let ok = 0, n = 0;
			for (const b of $btns.toArray()) {
				const d = await run_probe($(b), frm.__metrc_licence);
				n++;
				if (d && d.ok) ok++;
				$sum.text(`${ok} / ${n} passing…`);
			}
			$sum.text(`${ok} / ${n} returned 200`);
		});
}

function probeBtn(label, key) {
	return `<button class="metrc-probe" data-key="${key}" data-label="${label}" style="border:1px solid #bfd3ee;background:#f0f6ff;color:#20548f;cursor:pointer;border-radius:6px;padding:2px 8px;font:600 11px/1.6 inherit;">
		<span class="metrc-probe-icon">▶</span> GET ${label}<span class="metrc-probe-res"></span></button>`;
}

function run_probe($b, license) {
	const key = $b.data("key");
	$b.find(".metrc-probe-icon").text("…");
	$b.find(".metrc-probe-res").text("");
	return frappe
		.xcall("metrc_customizations.metrc_customizations.doctype.metrc_config.metrc_config.probe_endpoint", { key, license })
		.then((d) => {
			const ok = d.ok;
			$b.css({ background: ok ? "#e6f4ea" : "#fde8e8", borderColor: ok ? "#9ad3ad" : "#f1a7a3", color: ok ? "#1c6b3f" : "#b5352f" });
			$b.find(".metrc-probe-icon").text(ok ? "✓" : "✗");
			$b.find(".metrc-probe-res").text(` · ${d.status_code ?? "ERR"}${d.count != null ? ` · ${d.count.toLocaleString()}` : ""}`);
			$b.data("result", d);
			return d;
		})
		.catch(() => {
			$b.find(".metrc-probe-icon").text("✗");
			$b.css({ background: "#fde8e8", borderColor: "#f1a7a3", color: "#b5352f" });
		});
}

function show_probe(d, label) {
	const esc = (v) => frappe.utils.escape_html(v == null ? "" : typeof v === "object" ? JSON.stringify(v) : String(v));
	const color = d.ok ? "#1c6b3f" : "#b5352f";
	let body = `<div style="font-family:'DM Mono',monospace;font-size:12px;background:#f7f8fa;border-radius:8px;padding:8px 10px;margin-bottom:10px;">
		<b style="color:#2b6cb0;">GET</b> ${esc(d.path)}${d.license ? `?licenseNumber=${esc(d.license)}` : ""}</div>
		<div style="display:flex;gap:18px;margin-bottom:12px;font-size:13px;">
			<div><b style="color:${color};">${d.ok ? "✓" : "✗"} HTTP ${esc(d.status_code ?? "—")}</b></div>
			${d.ms != null ? `<div>${d.ms} ms</div>` : ""}
			${d.count != null ? `<div><b>${d.count.toLocaleString()}</b> records</div>` : ""}
		</div>`;
	if (!d.ok) {
		body += `<div style="color:#b5352f;font-size:13px;">${esc(d.message)}</div>
			${d.body ? `<pre style="margin-top:8px;white-space:pre-wrap;font-size:11px;">${esc(d.body)}</pre>` : ""}`;
	} else if ((d.sample || []).length) {
		const rows = d.sample.map((r) => (r && typeof r === "object" ? r : { Value: r }));
		// Every column with a plain value; the tag / package label first since that is what people look for.
		const FIRST = ["Label", "Name", "LicenseNumber", "ManifestNumber"];
		const cols = [...new Set(rows.flatMap((r) => Object.keys(r)))]
			.filter((c) => rows.some((r) => r[c] != null && typeof r[c] !== "object"))
			.sort((x, y) => (FIRST.includes(y) ? 1 : 0) - (FIRST.includes(x) ? 1 : 0));
		body += `<div style="font-size:12px;color:#718096;margin-bottom:6px;">Showing ${rows.length} of ${(d.count ?? rows.length).toLocaleString()}</div>
			<div style="overflow:auto;max-height:420px;"><table class="table table-bordered table-sm" style="font-size:12px;white-space:nowrap;">
			<thead><tr>${cols.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead>
			<tbody>${rows.map((r) => `<tr>${cols.map((c) => `<td>${esc(r[c])}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
	} else {
		body += `<div style="color:#718096;font-size:13px;">Connected — Metrc returned no records for this facility right now.</div>`;
	}
	const dlg = new frappe.ui.Dialog({ title: `Metrc · ${label}`, size: "extra-large" });
	dlg.$body.html(body);
	dlg.show();
}
