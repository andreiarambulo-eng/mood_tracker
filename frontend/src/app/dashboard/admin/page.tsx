"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { ApiResponse, PaginatedResponse } from "@/lib/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface AdminOverview {
  total_users: number;
  total_entries: number;
  this_week_avg_mood: number | null;
  this_week_entries: number;
}

interface AdminUser {
  user_id: string;
  full_name: string;
  email: string;
  role: "Admin" | "User";
  is_active: boolean;
  last_login: string | null;
}

function formatLastLogin(dateStr: string | null): string {
  if (!dateStr) return "Never";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function ChevronLeftIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}

function ChevronRightIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
}

function OverviewCards({ overview }: { overview: AdminOverview }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <Card className="glass-card border-0">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Total Users
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-foreground">
            {overview.total_users}
          </p>
        </CardContent>
      </Card>

      <Card className="glass-card border-0">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Total Entries
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-foreground">
            {overview.total_entries}
          </p>
        </CardContent>
      </Card>

      <Card className="glass-card border-0">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            This Week Avg Mood
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-foreground">
            {overview.this_week_avg_mood !== null
              ? overview.this_week_avg_mood.toFixed(1)
              : "—"}
          </p>
        </CardContent>
      </Card>

      <Card className="glass-card border-0">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            This Week Entries
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-foreground">
            {overview.this_week_entries}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

const PAGE_SIZE = 10;

function UserTable() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<PaginatedResponse<AdminUser>>(
        `/users/get?page=${page}&limit=${PAGE_SIZE}`
      );
      setUsers(res.data.data);
      setTotalPages(res.data.pagination.total_pages);
      setTotalCount(res.data.pagination.total_count);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  async function handleToggleActive(user: AdminUser) {
    setTogglingId(user.user_id);
    try {
      await api.patch<ApiResponse<AdminUser>>("/users/edit", {
        user_id: user.user_id,
        is_active: !user.is_active,
      });
      // Optimistically update local state
      setUsers((prev) =>
        prev.map((u) =>
          u.user_id === user.user_id ? { ...u, is_active: !u.is_active } : u
        )
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to update user");
    } finally {
      setTogglingId(null);
    }
  }

  return (
    <Card className="glass-card border-0">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-foreground">User Management</CardTitle>
          <span className="text-sm text-muted-foreground">
            {totalCount} user{totalCount !== 1 ? "s" : ""}
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground border-t-foreground" />
          </div>
        ) : error ? (
          <div className="px-6 py-4 text-sm text-destructive">{error}</div>
        ) : (
          <>
            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Last Login
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {users.length === 0 ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="px-6 py-8 text-center text-muted-foreground"
                      >
                        No users found.
                      </td>
                    </tr>
                  ) : (
                    users.map((user, idx) => (
                      <tr
                        key={user.user_id}
                        className={`border-b border-border/50 hover:bg-muted/20 transition-colors ${
                          idx % 2 === 0 ? "" : "bg-muted/5"
                        }`}
                      >
                        <td className="px-6 py-3 font-medium text-foreground">
                          {user.full_name}
                        </td>
                        <td className="px-6 py-3 text-muted-foreground">
                          {user.email}
                        </td>
                        <td className="px-6 py-3">
                          <Badge
                            variant="outline"
                            className={
                              user.role === "Admin"
                                ? "border-blue-500/40 text-blue-400"
                                : "border-border text-muted-foreground"
                            }
                          >
                            {user.role}
                          </Badge>
                        </td>
                        <td className="px-6 py-3">
                          <Badge
                            variant="outline"
                            className={
                              user.is_active
                                ? "border-green-500/40 text-green-400"
                                : "border-red-500/40 text-red-400"
                            }
                          >
                            {user.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </td>
                        <td className="px-6 py-3 text-muted-foreground text-xs">
                          {formatLastLogin(user.last_login)}
                        </td>
                        <td className="px-6 py-3 text-right">
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={togglingId === user.user_id}
                            onClick={() => handleToggleActive(user)}
                            className={
                              user.is_active
                                ? "border-red-500/40 text-red-400 hover:bg-red-500/10 hover:text-red-300"
                                : "border-green-500/40 text-green-400 hover:bg-green-500/10 hover:text-green-300"
                            }
                          >
                            {togglingId === user.user_id ? (
                              <span className="flex items-center gap-1">
                                <span className="h-3 w-3 animate-spin rounded-full border border-current border-t-transparent" />
                                Saving
                              </span>
                            ) : user.is_active ? (
                              "Deactivate"
                            ) : (
                              "Activate"
                            )}
                          </Button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-border">
                <span className="text-sm text-muted-foreground">
                  Page {page} of {totalPages}
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page === 1}
                    onClick={() => setPage((p) => p - 1)}
                    className="border-border text-muted-foreground"
                  >
                    <ChevronLeftIcon />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page === totalPages}
                    onClick={() => setPage((p) => p + 1)}
                    className="border-border text-muted-foreground"
                  >
                    <ChevronRightIcon />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default function AdminPage() {
  const { user, loading: authLoading } = useAuth(true);
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(false);
  const [overviewError, setOverviewError] = useState<string | null>(null);

  useEffect(() => {
    if (!user || user.role !== "Admin") return;

    async function fetchOverview() {
      setOverviewLoading(true);
      setOverviewError(null);
      try {
        const res = await api.get<ApiResponse<AdminOverview>>(
          "/admin/analytics/overview"
        );
        setOverview(res.data);
      } catch (e) {
        setOverviewError(
          e instanceof Error ? e.message : "Failed to load overview"
        );
      } finally {
        setOverviewLoading(false);
      }
    }

    fetchOverview();
  }, [user]);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground border-t-foreground" />
      </div>
    );
  }

  if (!user || user.role !== "Admin") {
    return (
      <div className="flex items-center justify-center py-20">
        <Card className="bg-card border-border w-full max-w-sm">
          <CardHeader>
            <CardTitle className="text-destructive text-center">
              Access Denied
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-muted-foreground text-sm">
              You do not have permission to view this page. This area is
              restricted to administrators only.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Admin Panel</h1>
        <p className="text-muted-foreground mt-1">
          Platform overview and user management.
        </p>
      </div>

      {/* Overview stats */}
      {overviewLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="bg-card border-border animate-pulse">
              <CardHeader className="pb-2">
                <div className="h-3 bg-muted/40 rounded w-24" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted/40 rounded w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : overviewError ? (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 px-5 py-4 text-sm text-destructive">
          {overviewError}
        </div>
      ) : overview ? (
        <OverviewCards overview={overview} />
      ) : null}

      {/* User management table */}
      <UserTable />
    </div>
  );
}
