import React, { useEffect, useState, useMemo } from "react";
import { useModelState, useModel } from "@anywidget/react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { RecursiveRenderer } from "./layout/recursive";
import { Parameters } from "./Parameters.tsx";
import { Progress } from "@/components/ui/progress";
import { Play, Square, Download, Copy, Terminal, CheckCircle2, Circle, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";
import Anser from "anser";

import type { PipelineConfig, StatusState, UIElement, WidgetMessage, ProgressState, Step } from "../types";

// --- Types ---

export const PipelineWidget: React.FC = () => {
    const model = useModel();
    const [config] = useModelState<PipelineConfig>("config");
    const [statusState, setStatusState] = useModelState<StatusState>("status_state");
    const [logs] = useModelState<string>("logs");
    const [resultFileName] = useModelState<string>("result_file_name");
    const [resultFileData] = useModelState<string>("result_file_data");
    const [progress] = useModelState<ProgressState>("progress");

    // Layout support
    const [layout] = useModelState<UIElement>("layout");
    const [paramsValues] = useModelState<Record<string, unknown>>("params_values");

    // Signals
    const [, setRunRequested] = useModelState<boolean>("run_requested");


    // Local State
    const [localLogs, setLocalLogs] = useState<string>("");
    const [showSteps, setShowSteps] = useState<boolean>(false);

    const isRunning = statusState === "running";

    // --- Logic ---

    // Polling Effect
    const offsetRef = React.useRef(0);
    const isRunningRef = React.useRef(false);

    useEffect(() => {
        offsetRef.current = localLogs.length;
    }, [localLogs]);

    // Keep ref in sync with state
    useEffect(() => {
        isRunningRef.current = statusState === "running";
    }, [statusState]);

    useEffect(() => {
        let pollInterval: ReturnType<typeof setInterval> | null = null;

        const poll = () => {
            if (model && isRunningRef.current) {
                model.send({ type: "poll", offset: offsetRef.current });
            }
        };

        if (statusState === "running") {
            pollInterval = setInterval(poll, 100); 
            poll(); 
        } else {
            if (model) {
                model.send({ type: "poll", offset: offsetRef.current });
            }
        }

        return () => {
            if (pollInterval) {
                clearInterval(pollInterval);
            }
        };
    }, [statusState, model]);


    // Message Handler - primary log delivery while running
    useEffect(() => {
        if (!model) return;

        const handleMsg = (msg: WidgetMessage) => {
            if (msg.type === "log_batch") {
                if (msg.content) {
                    // Append new content, update offset
                    setLocalLogs(prev => {
                        const newLogs = prev + msg.content;
                        offsetRef.current = newLogs.length;
                        return newLogs;
                    });
                }
                if (msg.status) {
                    setStatusState(msg.status);
                }
            } else if (msg.type === "run_finished") {
                // Final sync - use complete logs from backend
                if (msg.logs) {
                    setLocalLogs(msg.logs);
                    offsetRef.current = msg.logs.length;
                }
                if (msg.status) setStatusState(msg.status);
            }
        };

        model.on("msg:custom", handleMsg);
        return () => {
            model.off("msg:custom", handleMsg);
        };
    }, [model, setStatusState]); 



    // Sync logs from traitlet - only when NOT running to avoid duplicates
    useEffect(() => {
        if (logs === "") {
            if (localLogs !== "") {
                // eslint-disable-next-line react-hooks/set-state-in-effect
                setLocalLogs("");
                offsetRef.current = 0;
            }
        } else if (!isRunning && logs && logs !== localLogs) {
            // Only sync from traitlet when idle (avoids duplicate with message push)
            setLocalLogs(logs);
            offsetRef.current = logs.length;
        }
    }, [logs, isRunning, localLogs]);


    const handleRun = () => {
        setLocalLogs("");
        setStatusState("running"); 
        setRunRequested(true);
        model.save_changes();
    };

    const handleAbort = () => {
        model.set("terminate_requested", true);
        model.save_changes();
    };

    const handleDownload = () => {
        if (resultFileData) {
            const a = document.createElement("a");
            a.href = resultFileData;
            a.download = resultFileName;
            a.click();
        } else {
            model.send({ type: "download" });
        }
    };

    const copyLogs = () => {
        // eslint-disable-next-line no-control-regex
        const cleanLogs = localLogs.replace(/\u001b\[[0-9;]*m/g, "");
        navigator.clipboard.writeText(cleanLogs);
    };

    // Auto-scroll Effect
    const scrollRef = React.useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "instant" });
        }
    }, [localLogs]);

    return (
        <Card className="w-full max-w-4xl mx-auto shadow-md border-border bg-card text-card-foreground">
            <CardHeader className="bg-muted/50 border-b border-border pb-4">
                <div className="flex flex-wrap justify-between items-start gap-3">
                    <div className="min-w-0 flex-1">
                        <CardTitle className="text-lg sm:text-xl font-bold flex items-center gap-2">
                            <Terminal className="w-5 h-5 text-primary flex-shrink-0" />
                            <span className="truncate">{config?.title || "Pipeline Launcher"}</span>
                        </CardTitle>
                        <CardDescription className="mt-1 text-sm">
                            {config?.subtitle || "Configure and run your analysis pipeline"}
                        </CardDescription>
                    </div>
                    <Badge variant={
                        statusState === "running" ? "default" :
                            statusState === "error" || statusState === "aborted" ? "destructive" : "secondary"
                    } className={cn("uppercase tracking-wider font-semibold flex-shrink-0",
                        statusState === "finished" && "bg-emerald-500 hover:bg-emerald-600 border-transparent text-primary-foreground",
                        statusState === "running" && "bg-blue-500 hover:bg-blue-600"
                    )}>
                        {statusState}
                    </Badge>
                </div>
            </CardHeader>

            <CardContent className="p-6">
                {layout && Object.keys(layout).length > 0 ? (
                    <RecursiveRenderer node={layout} model={model} values={paramsValues} />
                ) : (
                    <Parameters model={model} />
                )}

                <div className="mt-8 flex flex-wrap justify-end items-center gap-3">
                    {resultFileName && (
                        <Button variant="outline" onClick={handleDownload} className="gap-2 border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800">
                            <Download className="w-4 h-4" />
                            Download Results
                        </Button>
                    )}

                    {!isRunning ? (
                        <Button onClick={handleRun} className="gap-2 bg-indigo-600 hover:bg-indigo-700 text-white min-w-[140px]">
                            <Play className="w-4 h-4" />
                            Run Pipeline
                        </Button>
                    ) : (
                        <Button onClick={handleAbort} variant="destructive" className="gap-2 min-w-[140px]">
                            <Square className="w-4 h-4 fill-current" />
                            Abort
                        </Button>
                    )}
                </div>

                {/* Progress Tracking UI - Toggleable */}
                {progress && progress.steps && progress.steps.length > 0 && (
                    <div className="mt-8 space-y-4 bg-slate-50 p-4 rounded-xl border border-slate-100 shadow-sm transition-all duration-300">
                        <div className="flex flex-wrap justify-between items-center gap-2 mb-1">
                            <div className="flex flex-wrap items-center gap-2 cursor-pointer select-none group" onClick={() => setShowSteps(!showSteps)}>
                                <span className="text-sm font-semibold text-slate-700 uppercase tracking-tight">Pipeline Progress</span>
                                <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 group-hover:text-slate-600 transition-colors uppercase tracking-tighter">
                                    {showSteps ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                                    {showSteps ? "HIDE STEPS" : "SHOW STEPS"}
                                </div>
                            </div>
                            <span className="text-xs font-bold text-blue-600">{Math.round(progress.percent)}%</span>
                        </div>
                        <Progress value={progress.percent} className="h-2 bg-slate-200" indicatorClassName="bg-blue-600" />
                        
                        {showSteps && (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pt-2 animate-in fade-in slide-in-from-top-1 duration-200">
                                {progress.steps.map((step: Step, i: number) => {
                                    const isCurrent = progress.current === step.name;
                                    const isCompleted = step.status === "completed";
                                    const isFailed = step.status === "failed";
                                    
                                    return (
                                        <div key={i} className={cn(
                                            "flex items-center gap-2.5 px-3 py-2 rounded-lg border text-[11px] transition-all",
                                            isCurrent ? "bg-indigo-50 border-indigo-200 text-indigo-700 shadow-sm ring-1 ring-indigo-200 scale-[1.02]" :
                                            isCompleted ? "bg-emerald-50 border-emerald-100 text-emerald-700" :
                                            isFailed ? "bg-red-50 border-red-100 text-red-700" :
                                            "bg-white border-slate-100 text-slate-400 opacity-60"
                                        )}>
                                            {isCompleted ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" /> :
                                             isFailed ? <Circle className="w-3.5 h-3.5 text-red-500 shrink-0" /> :
                                             isCurrent ? <Loader2 className="w-3.5 h-3.5 text-indigo-500 animate-spin shrink-0" /> :
                                             <Circle className="w-3.5 h-3.5 text-slate-300 shrink-0" />}
                                            
                                            <div className="flex flex-col min-w-0">
                                                <span className="font-bold truncate leading-tight uppercase tracking-tighter">{step.name}</span>
                                                {step.duration && <span className="text-[9px] opacity-70 font-medium">{step.duration}</span>}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}

                {/* Execution Logs - Integrated Header */}
                <div className="mt-8">
                    <Card className="bg-slate-950 text-slate-200 overflow-hidden border-slate-200 shadow-inner">
                        <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                <Terminal className="w-3 h-3" />
                                Execution Logs
                            </span>
                            <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={copyLogs} 
                                className="h-6 text-[9px] gap-1.5 text-slate-500 hover:text-slate-300 font-bold uppercase tracking-tighter hover:bg-slate-800"
                            >
                                <Copy className="w-3 h-3" /> COPY LOGS
                            </Button>
                        </div>

                        <ScrollArea className="h-[250px] w-full font-mono text-xs p-4">
                            <LogViewer content={localLogs} />
                            <div ref={scrollRef} />
                        </ScrollArea>
                        
                        {/* DEBUG SECTION */}
                        <details className="px-4 py-1.5 bg-slate-900/50 text-[9px] text-slate-500 border-t border-slate-800">
                            <summary className="cursor-pointer hover:text-slate-300 transition-colors">Internal State Debug</summary>
                            <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 pb-1">
                                <div>Status: <span className="text-slate-400">{statusState}</span></div>
                                <div>Traitlet Buffer: <span className="text-slate-400">{logs?.length || 0} bytes</span></div>
                                <div>Local Buffer: <span className="text-slate-400">{localLogs.length} bytes</span></div>
                                <div className="flex items-center gap-2">
                                    <span>Sync:</span>
                                    <button className="text-indigo-400 hover:text-indigo-300 underline" onClick={() => model.send({ type: "poll", offset: 0 })}>
                                        Force Manual Poll
                                    </button>
                                </div>
                            </div>
                        </details>
                    </Card>
                </div>
            </CardContent>
        </Card>
    );
};

const MAX_LOG_LENGTH = 50000; 

const LogViewer: React.FC<{ content: string }> = React.memo(({ content }) => {
    const html = useMemo(() => {
        let textToRender = content || "";
        if (textToRender.length > MAX_LOG_LENGTH) {
            const slicePoint = textToRender.length - MAX_LOG_LENGTH;
            const firstNewline = textToRender.indexOf('\n', slicePoint);
            textToRender = "..." + (firstNewline > -1 ? textToRender.slice(firstNewline + 1) : textToRender.slice(slicePoint));
        }

        return Anser.ansiToHtml(textToRender, { use_classes: false });
    }, [content]);

    return (
        <div
            className="whitespace-pre-wrap break-all leading-relaxed font-mono text-xs"
            dangerouslySetInnerHTML={{ __html: html || "<span class='text-slate-600 italic'>Ready...</span>" }}
        />
    );
});
