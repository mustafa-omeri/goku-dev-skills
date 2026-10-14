---
name: musgoku-next-safe-action
description: >
  Next.js Server Actions için next-safe-action kütüphanesi standartları.
  Tip güvenliği, Zod şema validasyonu, middleware zinciri, hata yönetimi ve optimistic updates.
---

# 🛡️ MuSGoKu — Next Safe Action & Type-Safe Server Actions

> **Kullanım Amacı:** Bu skill, Next.js ortamında form gönderimleri, mutasyonlar ve sunucu taraflı işlemler yapılırken `next-safe-action` kullanım standartlarını belirler.

---

## ⚙️ 1. Safe Action Client Yapılandırması (`lib/safe-action.ts`)

```ts
import { createSafeActionClient, DEFAULT_SERVER_ERROR_MESSAGE } from "next-safe-action";
import { z } from "zod";

// Base action client
export const actionClient = createSafeActionClient({
  handleServerError(e) {
    console.error("Server Action Hatası:", e.message);

    if (e instanceof CustomBusinessError) {
      return e.message;
    }

    return DEFAULT_SERVER_ERROR_MESSAGE;
  },
  defaultValidationErrorsShape: "flattened", // Client için kolay okunabilir fieldErrors ve formErrors
});

// Kimlik doğrulamalı (Auth) middleware'li Action Client
export const authActionClient = actionClient.use(async ({ next }) => {
  const session = await getSession(); // Auth kontrolü

  if (!session?.user?.id) {
    throw new Error("Oturum açmanız gerekmektedir.");
  }

  return next({
    ctx: {
      userId: session.user.id,
      role: session.user.role,
    },
  });
});
```

---

## 📝 2. Server Action Tanımlama Deseni

```ts
// src/features/company/actions/update-company.ts
"use server";

import { z } from "zod";
import { authActionClient } from "@/lib/safe-action";
import { revalidateTag } from "next/cache";

const updateCompanySchema = z.object({
  companyId: z.string().uuid({ message: "Geçersiz şirket ID formatı" }),
  name: z.string().min(2, { message: "Şirket adı en az 2 karakter olmalıdır" }),
  industry: z.string().optional(),
});

export const updateCompanyAction = authActionClient
  .schema(updateCompanySchema)
  .action(async ({ parsedInput: { companyId, name, industry }, ctx: { userId } }) => {
    // 1. Yetki kontrolü veya DB işlemi
    const updated = await db.company.update({
      where: { id: companyId, createdBy: userId },
      data: { name, industry },
    });

    // 2. Next.js cache geçersiz kılma
    revalidateTag(`company-${companyId}`);

    // 3. Tip güvenli dönüş
    return {
      success: true,
      company: updated,
    };
  });
```

---

## 💻 3. Client Component İçinde Tüketim (`useAction`)

### React Hook Form veya Buton ile Entegrasyon:
```tsx
"use client";

import { useAction } from "next-safe-action/hooks";
import { updateCompanyAction } from "@/features/company/actions/update-company";
import { toast } from "sonner";

export function EditCompanyForm({ companyId, initialName }: { companyId: string; initialName: string }) {
  const { execute, isExecuting, result } = useAction(updateCompanyAction, {
    onSuccess({ data }) {
      toast.success("Şirket bilgisi başarıyla güncellendi.");
    },
    onError({ error }) {
      if (error.validationErrors) {
        toast.error("Girdiğiniz bilgileri kontrol ediniz.");
      } else if (error.serverError) {
        toast.error(error.serverError);
      }
    },
  });

  const onSubmit = (formData: FormData) => {
    execute({
      companyId,
      name: formData.get("name") as string,
    });
  };

  return (
    <form action={onSubmit} className="space-y-4">
      <input name="name" defaultValue={initialName} className="input" />
      <button type="submit" disabled={isExecuting} className="btn-primary">
        {isExecuting ? "Kaydediliyor..." : "Kaydet"}
      </button>
    </form>
  );
}
```

---

## 🔄 4. TanStack Query ile Birlikte Kullanım

Next.js Server Actions, `@tanstack/react-query` v5 mutation fonksiyonları içinde `executeAsync` ile çağrılarak tam entegrasyon sağlanabilir:

```ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateCompanyAction } from "./actions";

export function useUpdateCompanyMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { companyId: string; name: string }) => {
      const res = await updateCompanyAction(variables);
      if (res?.serverError) throw new Error(res.serverError);
      if (res?.validationErrors) throw new Error("Doğrulama hatası");
      return res?.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["company", variables.companyId] });
    },
  });
}
```
