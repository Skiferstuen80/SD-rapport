import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";

interface ReportRequest {
  reportType: "month" | "quarter" | "year";
  year: number;
  quarter?: string;
  month?: number;
}

export async function POST(request: NextRequest) {
  try {
    const body: ReportRequest = await request.json();
    const { reportType = "quarter", year = 2025, quarter = "Q4", month } = body;

    const args = [
      "-m",
      "hms_report",
      "--type",
      reportType,
      "--year",
      String(year),
      "--output-json",
    ];

    if (reportType === "quarter") {
      args.push("--quarter", quarter || "Q4");
    } else if (reportType === "month") {
      if (!month) {
        return NextResponse.json(
          { error: "month kreves for rapporttype 'month'" },
          { status: 400 }
        );
      }
      args.push("--month", String(month));
    }

    const result = await new Promise<{ filename: string; docx_base64: string }>(
      (resolve, reject) => {
        const proc = spawn("python", args, {
          cwd: process.cwd(),
          env: {
            ...process.env,
            PYTHONIOENCODING: "utf-8",
          },
        });

        const chunks: Buffer[] = [];
        const errChunks: Buffer[] = [];

        proc.stdout.on("data", (data: Buffer) => chunks.push(data));
        proc.stderr.on("data", (data: Buffer) => errChunks.push(data));

        proc.on("close", (code) => {
          if (code !== 0) {
            const stderr = Buffer.concat(errChunks).toString("utf-8");
            reject(new Error(`Python avsluttet med kode ${code}: ${stderr}`));
            return;
          }
          try {
            const stdout = Buffer.concat(chunks).toString("utf-8");
            resolve(JSON.parse(stdout));
          } catch (e) {
            reject(new Error(`Kunne ikke parse Python-output: ${e}`));
          }
        });

        proc.on("error", (err) => {
          reject(new Error(`Kunne ikke starte Python: ${err.message}`));
        });
      }
    );

    const docxBuffer = Buffer.from(result.docx_base64, "base64");

    return new NextResponse(docxBuffer, {
      status: 200,
      headers: {
        "Content-Type":
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "Content-Disposition": `attachment; filename="${result.filename}"`,
      },
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Ukjent feil ved rapportgenerering";
    console.error("HMS report error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
