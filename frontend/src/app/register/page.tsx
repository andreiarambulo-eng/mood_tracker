"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register } from "@/lib/auth";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      await register(email, fullName, password);
      router.push("/login");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500/20 to-blue-500/20 border border-violet-500/20 mb-4 glow-purple">
            <span className="text-3xl">🌌</span>
          </div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight">
            Mood Tracker
          </h1>
          <p className="text-muted-foreground mt-1.5 text-sm">
            Start tracking your emotional well-being
          </p>
        </div>

        <div className="glass-card rounded-2xl p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-foreground">Create account</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Fill in your details to get started
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="rounded-xl bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-400">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="fullName" className="text-sm text-muted-foreground">Full Name</Label>
              <Input
                id="fullName"
                type="text"
                placeholder="Jane Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                autoComplete="name"
                disabled={loading}
                className="bg-white/5 border-white/10 focus:border-violet-500/50 h-11 rounded-xl"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm text-muted-foreground">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                disabled={loading}
                className="bg-white/5 border-white/10 focus:border-violet-500/50 h-11 rounded-xl"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm text-muted-foreground">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
                disabled={loading}
                className="bg-white/5 border-white/10 focus:border-violet-500/50 h-11 rounded-xl"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm text-muted-foreground">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
                disabled={loading}
                className="bg-white/5 border-white/10 focus:border-violet-500/50 h-11 rounded-xl"
              />
            </div>

            <Button
              type="submit"
              className="w-full h-11 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 text-white font-semibold shadow-lg shadow-violet-500/20 transition-all"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Creating account...
                </span>
              ) : "Create account"}
            </Button>
          </form>

          <p className="text-sm text-muted-foreground text-center mt-6">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-violet-400 font-medium hover:text-violet-300 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
