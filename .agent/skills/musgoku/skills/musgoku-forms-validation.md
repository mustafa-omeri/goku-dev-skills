---
name: musgoku-forms-validation
description: >
  Form oluşturma, validasyon ve submit yönetimi için best practices.
  React Hook Form + Zod + Shadcn UI Form bileşenleri ile uyumlu.
---

# 📝 MuSGoKu — Forms & Validation Best Practices

## React Hook Form + Zod Pattern

### Zod Schema Tanımlama
```tsx
// src/features/<feature>/schemas.ts
import { z } from 'zod';

export const createUserSchema = z.object({
  firstName: z.string()
    .min(2, 'İsim en az 2 karakter olmalıdır')
    .max(50, 'İsim en fazla 50 karakter olabilir'),
  lastName: z.string()
    .min(2, 'Soyad en az 2 karakter olmalıdır'),
  email: z.string()
    .email('Geçerli bir email adresi giriniz'),
  role: z.enum(['admin', 'manager', 'employee'], {
    error: 'Geçerli bir rol seçiniz',
  }),
  isActive: z.boolean().default(true),
  phone: z.string()
    .regex(/^(\+90|0)?[0-9]{10}$/, 'Geçerli bir telefon numarası giriniz')
    .optional(),
});

export type CreateUserFormData = z.infer<typeof createUserSchema>;
```

> **⛔ Sürüm notu (Zod):** Zod v3 ile v4 arasında hata mesanı API'si değişti.
> `errorMap` kaldırıldı; mesaj için `error` parametresi kullanılır.
> `z.string().email('mesaj')` v4'te çalışır, ancak yeni kodda ayrı `z.email({ error: 'mesaj' })`
> tercih edilir. **Kod yazmadan önce `package.json` içindeki Zod sürümünü oku.**
> Emin değilsen `context7`'den güncel API'yi sorgula — "hatırlıyorum" deme.

### Form Bileşeni Pattern
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { createUserSchema, type CreateUserFormData } from './schemas';

interface CreateUserFormProps {
  onSubmit: (data: CreateUserFormData) => void;
  isLoading?: boolean;
  defaultValues?: Partial<CreateUserFormData>;
}

export function CreateUserForm({ onSubmit, isLoading, defaultValues }: CreateUserFormProps) {
  const { t } = useTranslation();
  
  const form = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      role: 'employee',
      isActive: true,
      ...defaultValues,
    },
  });

  const handleSubmit = form.handleSubmit((data) => {
    onSubmit(data);
  });

  return (
    <Form {...form}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <FormField
          control={form.control}
          name="firstName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('user.firstName')}</FormLabel>
              <FormControl>
                <Input placeholder={t('user.firstNamePlaceholder')} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('user.role')}</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder={t('user.selectRole')} />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="admin">{t('roles.admin')}</SelectItem>
                  <SelectItem value="manager">{t('roles.manager')}</SelectItem>
                  <SelectItem value="employee">{t('roles.employee')}</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isLoading}>
          {isLoading ? t('common.saving') : t('common.save')}
        </Button>
      </form>
    </Form>
  );
}
```

### Form + Mutation Entegrasyonu
```tsx
import { useCreateUser } from './hooks/useCreateUser';

function CreateUserPage() {
  const { t } = useTranslation();
  const createUserMutation = useCreateUser();

  const handleSubmit = (data: CreateUserFormData) => {
    createUserMutation.mutate(data, {
      onSuccess: () => {
        toast.success(t('user.createSuccess'));
        navigate('/users');
      },
      onError: (error) => {
        toast.error(error.message);
      },
    });
  };

  return (
    <CreateUserForm
      onSubmit={handleSubmit}
      isLoading={createUserMutation.isPending}
    />
  );
}
```

## Kurallar

1. **Zod schema zorunlu** — Her form için Zod ile validasyon şeması tanımlanır.
2. **`zodResolver`** — `useForm` hook'unda resolver olarak kullanılır.
3. **Shadcn Form bileşenleri** — `<Form>`, `<FormField>`, `<FormItem>`, `<FormLabel>`, `<FormMessage>` kullanılır.
4. **Type inference** — Form data tipi `z.infer<typeof schema>` ile çıkarılır.
5. **i18n** — Tüm label ve placeholder'lar i18n key'leri ile gelir.
6. **Loading state** — Submit button'da `isPending` durumu gösterilir.
7. **Error handling** — Form seviyesinde ve field seviyesinde hata gösterimi yapılır.
8. **Controlled components** — Shadcn + Radix bileşenleri ile Controller veya render pattern kullanılır.

## Anti-Patterns

- ❌ Ham `<form>` + `<input>` kullanımı (Shadcn Form kullan)
- ❌ Manuel `onChange` handler'ları (React Hook Form yönetsin)
- ❌ İnline validasyon kuralları (Zod schema kullan)
- ❌ Form state'i için `useState` (React Hook Form kullan)
- ❌ Validasyon mesajlarının hardcode edilmesi (i18n kullan)
