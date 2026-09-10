<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class AdminUserSeeder extends Seeder
{
    public function run(): void
    {
        $email = env('ADMIN_EMAIL', 'admin@madeforte.local');
        $password = env('ADMIN_PASSWORD', 'admin123456');
        $super = filter_var(env('ADMIN_IS_SUPER', true), FILTER_VALIDATE_BOOLEAN);

        User::query()->updateOrCreate(
            ['email' => $email],
            [
                'name' => env('ADMIN_NAME', 'Super Admin'),
                'password' => Hash::make($password),
                'email_verified_at' => now(),
                'is_super_admin' => $super,
                'cliente_id' => $super ? null : 1,
            ]
        );
    }
}
