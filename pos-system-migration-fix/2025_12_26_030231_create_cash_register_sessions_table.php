<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        if (!Schema::hasTable('cash_register_sessions')) {
            Schema::create('cash_register_sessions', function (Blueprint $table) {
                $table->id();
                $table->foreignId('store_id')->constrained()->onDelete('cascade');
                $table->foreignId('user_id')->constrained()->onDelete('cascade'); // The "Custodian" who opened it
                $table->decimal('opening_amount', 10, 2);
                $table->decimal('closing_amount', 10, 2)->nullable();
                $table->decimal('expected_amount', 10, 2)->nullable();
                $table->decimal('variance', 10, 2)->nullable();
                $table->enum('status', ['open', 'closed'])->default('open');
                $table->timestamp('opened_at');
                $table->timestamp('closed_at')->nullable();
                $table->text('notes')->nullable();
                $table->timestamps();
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('cash_register_sessions');
    }
};
